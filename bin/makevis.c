#include "Python.h"
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/mman.h>

#define TRUE (1)
#define FALSE (0)

int fD;
const unsigned char *mapping;

static PyObject *makevis_open(PyObject *self, PyObject *args)
{
  int i;
  long long sts;
  struct stat s;
  size_t size;
  const char *fileName;

  if (!PyArg_ParseTuple(args, "s", &fileName))
    return NULL;
  fD = open(fileName, O_RDONLY);
  if (fD < 0) {
    fprintf(stderr, "makevis.open: error returned by open()\n");
    perror(fileName);
    exit(-1);
  }
  i = fstat(fD, &s);
  if (i != 0) {
    fprintf(stderr, "makevis.open: error returned by fstat()\n");
    perror(fileName);
    exit(-1);
  }
  size = s.st_size;
  mapping = mmap(NULL, size, PROT_READ, MAP_PRIVATE, fD, 0);
  if (mapping == MAP_FAILED) {
    fprintf(stderr, "makevis.open: error returned by mmap()\n");
    perror(fileName);
    exit(-1);
  }
  sts = size;
  return Py_BuildValue("l", sts);
}

static PyObject *makevis_scanno(PyObject *self, PyObject *args)
{
  long int offset;
  int newFormat, scanNo;

  if (!PyArg_ParseTuple(args, "li", &offset, &newFormat))
    return NULL;
  if (newFormat)
    scanNo = *((unsigned int *)&mapping[offset]);
  else
    scanNo = (mapping[offset]<<24) + (mapping[offset+1]<<16) + (mapping[offset+2]<<8) + mapping[offset+3];
  return Py_BuildValue("i", scanNo);
}

static PyObject *makevis_recsize(PyObject *self, PyObject *args)
{
  long int offset;
  int newFormat, recSize;

  if (!PyArg_ParseTuple(args, "li", &offset, &newFormat))
    return NULL;
  if (newFormat)
    recSize = *((unsigned int *)&mapping[offset+4]);
  else
    recSize = (mapping[offset+8]<<24) + (mapping[offset+9]<<16) + (mapping[offset+10]<<8) + mapping[offset+11];
  return Py_BuildValue("i", recSize);
}

static PyObject *makevis_scaleexp(PyObject *self, PyObject *args)
{
  int scaleExp;
  long int offset;
  int newFormat;

  if (!PyArg_ParseTuple(args, "li", &offset, &newFormat))
    return NULL;
  if (newFormat)
    scaleExp = *((unsigned short *)&mapping[offset]);
  else
    scaleExp = (mapping[offset+8]<<8) + mapping[offset+9];
  if (scaleExp > 32767)
    scaleExp -= 65536;
  return Py_BuildValue("i", scaleExp);
}

static PyObject *makevis_convert(PyObject *self, PyObject *args)
{
  static int firstCall = TRUE;
  long int offset, offsetInc, smallOffsetInc;
  int nPoints, newFormat, i, j, trim, first, last, reverse, chanAve, startChan, endChan, originalNPoints;
  int real = 0, imag = 0;
  double scale, weight, fReal, fImag, fChanAve;
  static PyObject *list;
  PyObject *num, *pyWeight;

  if (firstCall)
    firstCall = FALSE;
  else
    Py_DECREF(list);

  if (!PyArg_ParseTuple(args, "iidlidiiiiiii",
			&nPoints, &originalNPoints, &scale, &offset, &newFormat, &weight, &trim, &first, &last, &reverse, &chanAve, &startChan, &endChan)) {
    printf("NULL return 1\n");
    return NULL;
  }
  /* printf("%d %d %f %ld %d %f %d %d %d %d %d %d %d\n", nPoints, originalNPoints, scale, offset, newFormat, weight, trim, first, last, reverse, chanAve, startChan, endChan); */
	 
  if (newFormat)
    offset += 2;
  else
    offset += 10;
  list = PyList_New(3*nPoints);
  if (!list) {
    printf("NULL return 2\n");
    return NULL;
  }
  pyWeight = PyFloat_FromDouble(weight);
  if (!pyWeight) {
    Py_DECREF(list);
    printf("NULL return 3\n");
    return NULL;
  }
  if (reverse) {
    offset += (originalNPoints - startChan*chanAve - 1)*4;
    smallOffsetInc = -4;
  } else {
    offset += startChan*4*chanAve;
    smallOffsetInc = 4;
  }
  offsetInc = chanAve*smallOffsetInc;
  fChanAve = (double)chanAve;
  /* printf("startChan = %d, endChan = %d\n", startChan, endChan); */
  for (i = startChan; i <= endChan; i++) {
    /* printf("i = %d\n", i); */
    if ((weight <= 0.0) || (trim && ((i < first) || (i > last)))) {
      fReal = fImag = 0.0;
    } else {
      fReal = fImag = 0.0;
      for (j = 0; j < chanAve; j++) {
	if (newFormat) {
	  real = (float)(*((unsigned short *)&mapping[offset + smallOffsetInc*j]));
	  imag = (float)(*((unsigned short *)&mapping[offset+2 + smallOffsetInc*j]));
	} else {
	  real = (float)((mapping[offset + smallOffsetInc*j]<<8) + mapping[offset+1 + smallOffsetInc*j]);
	  imag = (float)((mapping[offset+2 + smallOffsetInc*j]<<8) + mapping[offset+3 + smallOffsetInc*j]);
	}
	if (real > 32767)
	  real -= 65536;
	if (imag > 32767)
	  imag -= 65536;
	fReal += (double)real;
	fImag += (double)imag;
      }
      fReal = fReal*scale/fChanAve;
      fImag = fImag*scale/fChanAve;
    }
    num = PyFloat_FromDouble(fReal);
    if (!num) {
      Py_DECREF(list);
      printf("NULL return 4\n");
      return NULL;
    }
    PyList_SET_ITEM(list, 3*(i-startChan), num);
    num = PyFloat_FromDouble(-fImag);
    if (!num) {
      Py_DECREF(list);
      printf("NULL return 5\n");
      return NULL;
    }
    /* printf("i = %d, 3*i+1 = %d, offset = %ld, inc = %ld\n", i, 3*i + 1, offset, offsetInc); */
    PyList_SET_ITEM(list, 3*(i-startChan) + 1, num);
    PyList_SET_ITEM(list, 3*(i-startChan) + 2, pyWeight);
    offset += offsetInc;
  }
  return Py_BuildValue("O", list);
}

static PyMethodDef MakevisMethods[] = {
  {"scaleexp",  makevis_scaleexp, METH_VARARGS,
   "Return the scaling exponent"},
  {"recsize",  makevis_recsize, METH_VARARGS,
   "Return the record size"},
  {"scanno",  makevis_scanno, METH_VARARGS,
   "Return the scan number"},
  {"open",  makevis_open, METH_VARARGS,
   "Open and mmap the sch_read file"},
  {"convert",  makevis_convert, METH_VARARGS,
   "Convert raw data to signed integers."},
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initmakevis(void)
{
  PyObject *m;
  
  m = Py_InitModule("makevis", MakevisMethods);
  if (m == NULL)
    return;
}
