#!/usr/bin/env python
# 
# Fit specflux with polynomial and 1d gaussians.
# 
# 

import os, sys, re, glob, copy, json, shutil
import astropy.constants as const
import astropy.units as u
import click
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.cm as cm
import matplotlib.patheffects
import numpy as np
import warnings
from astropy.io import fits
from astropy.modeling import models, fitting
from astropy.stats import sigma_clipped_stats
from astropy.table import Table
from astropy.visualization import simple_norm
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales, proj_plane_pixel_area
from collections import OrderedDict
import warnings
warnings.filterwarnings('ignore', category=UserWarning)
mpl.rcParams['font.size'] = 13
mpl.rcParams['axes.labelsize'] = 16
mpl.rcParams['axes.labelpad'] = 10
mpl.rcParams['legend.fontsize'] = 10


g_script_dir = os.path.abspath(os.path.dirname(__file__))



class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)




# option
# from https://stackoverflow.com/questions/48391777/nargs-equivalent-for-options-in-click
class OptionEatAll(click.Option):

    def __init__(self, *args, **kwargs):
        self.save_other_options = kwargs.pop('save_other_options', True)
        nargs = kwargs.pop('nargs', -1)
        assert nargs == -1, 'nargs, if set, must be -1 not {}'.format(nargs)
        super(OptionEatAll, self).__init__(*args, **kwargs)
        self._previous_parser_process = None
        self._eat_all_parser = None

    def add_to_parser(self, parser, ctx):

        def parser_process(value, state):
            # method to hook to the parser.process
            done = False
            value = [value]
            if self.save_other_options:
                # grab everything up to the next option
                while state.rargs and not done:
                    for prefix in self._eat_all_parser.prefixes:
                        if state.rargs[0].startswith(prefix):
                            done = True
                    if not done:
                        value.append(state.rargs.pop(0))
            else:
                # grab everything remaining
                value += state.rargs
                state.rargs[:] = []
            value = tuple(value)

            # call the actual process
            self._previous_parser_process(value, state)

        retval = super(OptionEatAll, self).add_to_parser(parser, ctx)
        for name in self.opts:
            our_parser = parser._long_opt.get(name) or parser._short_opt.get(name)
            if our_parser:
                self._eat_all_parser = our_parser
                self._previous_parser_process = our_parser.process
                our_parser.process = parser_process
                break
        
        return retval





def get_FWZI(
        specaxis, 
        specflux, 
        mean, 
        stddev,
    ):
    ileft = np.argmin(np.abs( specaxis - (mean - 2.35482*stddev) )) # -FWHM
    iright = np.argmin(np.abs( specaxis - (mean + 2.35482*stddev) )) # +FWHM
    while ileft >= 0:
        if specflux[ileft] < 0:
            break
        ileft -= 1
    while iright <= len(specaxis)-1:
        if specflux[iright] < 0:
            break
        iright += 1
    xleft = specaxis[ileft]
    xright = specaxis[iright]
    FWZI = np.abs(xright - xleft) / mean * 2.99792458e5 # km/s
    return (FWZI, xleft, xright)






@click.command()
@click.argument('spectrum_table_file', type=click.Path(exists=True))
@click.argument('output_json_file', type=click.Path(exists=False), default=None, required=False)
@click.option('--polynomial-order', type=int, default=5, help='Polynomial baseline order. Default is 5.')
@click.option('--line-centers', cls=OptionEatAll, default=None, help='Line centers. If None then take the peak position.')
@click.option('--line-names', cls=OptionEatAll, default=None, help='Line names. If None then name the lines by their order.')
@click.option('--freq-column', '--spec-axis-column', 'spec_axis_column', type=str, default=None, help='Frequency column name. If None then take the first column.')
@click.option('--flux-column', type=str, default=None, help='Flux column name. If None then take the second column.')
@click.option('--maxdeg', type=float, default=5, help='Polynomial degree, default is 5.')
def main(
        spectrum_table_file, 
        output_json_file, 
        polynomial_order, 
        line_centers, 
        line_names, 
        spec_axis_column, 
        flux_column, 
        maxdeg, 
    ):
    
    # read spectrum
    print('Reading {!r}'.format(spectrum_table_file))
    if re.match(r'.*\.(txt|dat|ascii)$', spectrum_table_file):
        spectrum_table = Table.read(spectrum_table_file, format='ascii.commented_header')
    else:
        spectrum_table = Table.read(spectrum_table_file)
    if spec_axis_column is None:
        spec_axis_column = spectrum_table.colnames[0]
    if flux_column is None:
        flux_column = spectrum_table.colnames[1]
    print('Reading column {!r} as spectral axis'.format(spec_axis_column))
    specaxis = spectrum_table[spec_axis_column]
    print('Reading column {!r} as spectrum flux'.format(flux_column))
    specflux = spectrum_table[flux_column]
    
    
    chanwidth = np.nanmean(np.diff(specaxis))
    
    
    # check output_json_file
    if output_json_file is None:
        output_json_file = os.path.splitext(spectrum_table_file)[0] + '.json'
    
    output_dir = os.path.dirname(output_json_file)
    if output_dir != '':
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
    
    
    # check user input line centers
    if isinstance(line_centers, str):
        line_centers = eval(line_centers)
    if line_centers is None:
        line_centers = []
    if len(line_centers) == 0:
        line_centers = [specaxis[np.argmax(specflux)]]
    else:
        line_centers = np.array(line_centers).astype(float)
    print('line_centers: {} (type: {})'.format(line_centers, type(line_centers)))
    
    
    # check user input line names
    if isinstance(line_names, str):
        line_names = eval(line_names)
    if line_names is None:
        line_names = []
    if len(line_names) == 0:
        line_names = ['line_{}'.format(i+1) for i in range(len(line_centers))]
    elif len(line_names) != len(line_centers):
        raise Exception('Error! The input line_names and line_centers should have the same number of elements!')
    print('line_names: {} (type: {})'.format(line_names, type(line_names)))
    
    
    # estimate valid continuum range for fitting
    no_fit_windows = [
        # (1.567, 1.572), 
        # (1.584, 1.591), 
        # (1.598, 1.617), 
        # (1.633, 1.646), 
        # (1.6557, 1.6600), 
        # (1.93, 1.94), 
        # (1.995, 2.025), 
        # (2.047, 2.079), 
        # (2.20, 2.22), 
    ]
    mean, median, stddev = sigma_clipped_stats(specflux)
    specmask = np.full(len(specflux), fill_value=False, dtype=bool) # True for channels to be excluded in the fitting
    for w1, w2 in no_fit_windows:
        specmask[np.logical_and(specaxis>w1, specaxis<w2)] = True
    
    
    
    # fit polynomial response curve:
    #     specflux * response_curve_from_polynomial_fit = template_flux
    polynomial_init = models.Polynomial1D(
        name='Polynomial', 
        degree=polynomial_order, 
        c0=median
    )
    polynomial_fitter = fitting.LevMarLSQFitter()
    valid = np.logical_and(
        np.isfinite(specflux), 
        np.invert(specmask)
    )
    polynomial_fitted = polynomial_fitter(
        polynomial_init, 
        specaxis[valid], 
        specflux[valid]
    )
    print('polynomial_fitted', polynomial_fitted)
    
    polynomial_flux = polynomial_fitted(specaxis)
    
    
    # get continuum-subtracted mean, med, rms
    contsub_mean, contsub_med, contsub_sig = sigma_clipped_stats(specflux-polynomial_flux)
    
    
    # add 1d gaussian lines
    composite_model_init = polynomial_fitted
    for i, line_center in enumerate(line_centers):
        ichan = np.argmin(np.abs(specaxis-line_center))
        composite_model_init += models.Gaussian1D(
            name=line_names[i],
            amplitude=specflux[ichan], 
            mean=line_center, 
            stddev=chanwidth*1.5,
        )
    
    
    # fit composite model with weights
    composite_model_fitter = fitting.LevMarLSQFitter(calc_uncertainties=True)
    valid = np.logical_and(
        np.isfinite(specflux), 
        np.invert(specmask)
    )
    composite_model_fitted = composite_model_fitter(
        composite_model_init, 
        specaxis[valid], 
        specflux[valid],
        maxiter=3000, 
        weights=1.0/np.full(np.count_nonzero(valid), fill_value=contsub_sig),
    )
    print('composite_model_fitted', composite_model_fitted)
    
    composite_model_flux = composite_model_fitted(specaxis)
    
    polynomial_flux = polynomial_fitted(specaxis) # TODO: update polynomial_fitted?
    
    
    # get uncertainties from covariance matrix
    #print('composite_model_fitter.fit_info', composite_model_fitter.fit_info)
    covariance_matrix = composite_model_fitter.fit_info['param_cov']
    param_uncertainties = {}
    if covariance_matrix is not None:
        free_param_uncertainties = np.diag(covariance_matrix)**0.5
        ifreepar = 0
        for ipar, parname in enumerate(composite_model_fitted.param_names):
            parvar = getattr(composite_model_fitted, parname)
            if not parvar.tied and not parvar.fixed:
                param_uncertainties[parname] = free_param_uncertainties[ifreepar]
                ifreepar += 1
    
    
    
    # 
    # prepare figure
    ncols = 1 # one column panels
    nrows = 2 # one row
    #print('ncols, nrows = {}, {}, {}'.format(ncols, nrows))
    w = 12.0 # panel width in inches
    h = 3.0 # panel height in inches
    dw = 0.6 # panel width spacing in inches
    dh = 0.6 # panel height spacing in inches
    figleft = 1.35 # margin in inches, 
    figright = 0.35 # margin in inches
    figtop = 0.8 # margin in inches
    figbottom = 0.8 # margin in inches
    width_ratios = np.array([1.,]) # first must be 1.
    height_ratios = np.array([1., 0.6]) # first must be 1.
    wspace = dw / (w * np.mean(width_ratios)) # absolute inches
    hspace = dh / (h * np.mean(height_ratios)) # absolute inches
    figwidth = np.sum(w*width_ratios) + (dw*(ncols-1)) + figleft + figright
    figheight = np.sum(h*height_ratios) + (dh*(nrows-1)) + figtop + figbottom
    #print('figsize', (figwidth, figheight))
    fig, axes = plt.subplots(
        ncols=ncols, nrows=nrows, figsize=(figwidth, figheight), 
        gridspec_kw=dict(
            left=figleft/figwidth, right=1.-figright/figwidth, 
            bottom=figbottom/figheight, top=1.-figtop/figheight, 
            width_ratios=width_ratios, height_ratios=height_ratios,
            wspace=wspace, hspace=hspace
        )
    )
    
    
    # 
    # plot specflux
    ax = axes[0]
    ax.set_ylabel('Flux')
    ax.plot(specaxis, specflux, lw=1.0, color='C0', label='data')
    ax.plot(specaxis, composite_model_flux, color='C1', lw=2.5, alpha=0.7, label='fit')
    ax.set_xlim([np.nanmin(specaxis[valid]), np.nanmax(specaxis[valid])])
    ax.xaxis.set_major_locator(ticker.MaxNLocator(20))
    ax.legend()
    
    
    # 
    # plot residual
    ax = axes[1]
    ax.set_ylabel('Residual')
    ax.plot(specaxis, specflux-composite_model_flux, lw=1.0, color='C0', label='residual')
    ax.set_xlim([np.nanmin(specaxis[valid]), np.nanmax(specaxis[valid])])
    ax.xaxis.set_major_locator(ticker.MaxNLocator(20))
    ax.legend()
    
    
    # 
    # save json info
    output_info = {}
    for parname in composite_model_fitted.param_names:
        parvar = getattr(composite_model_fitted, parname)
        if parname in param_uncertainties:
            parvar.error = param_uncertainties[parname]
        else:
            parvar.error = np.nan
        regmatch = re.match(r'^amplitude_([0-9]+)$', parname)
        if regmatch:
            icomp = int(regmatch.group(1))
            iline = icomp-1
            output_info['line_name_{}'.format(icomp)] = line_names[iline]
        output_info[parname] = parvar.value
        output_info[parname+'_err'] = parvar.error
        regmatch = re.match(r'^stddev_([0-9]+)$', parname)
        if regmatch:
            icomp = int(regmatch.group(1))
            mean = output_info['mean_{}'.format(icomp)]
            stddev = output_info['stddev_{}'.format(icomp)]
            FWZI, xleft, xright = get_FWZI(
                specaxis, 
                specflux - polynomial_flux, 
                mean, 
                stddev,
            )
            output_info['FWHM_{}'.format(icomp)] = 2.35482*(stddev/mean*2.99792458e5) # km/s
            output_info['FWZI_{}'.format(icomp)] = FWZI
            output_info['FWHM_{}_unit'.format(icomp)] = 'km/s'
            output_info['FWZI_{}_unit'.format(icomp)] = 'km/s'
    with open(output_json_file, 'w') as fp:
       json.dump(output_info, fp, indent=4, cls=NumpyEncoder)
    print('Output to {!r}'.format(output_json_file))
    
    
    # 
    # output figure
    output_figure = os.path.splitext(output_json_file)[0] + '.pdf'
    fig.savefig(output_figure, dpi=300)
    print('Output to {!r}'.format(output_figure))
    if output_figure.endswith('.pdf'):
        output_figure_png = re.sub(r'\.pdf$', r'.png', output_figure)
        fig.savefig(output_figure_png, dpi=300)
        print('Output to {!r}'.format(output_figure_png))
    






if __name__ == '__main__':
    
    main()





















