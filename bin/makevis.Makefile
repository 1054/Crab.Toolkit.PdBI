gcc -O3 -Wall -fPIC -shared /System/Library/Frameworks/Python.framework/Versions/2.7/lib/libpython2.7.dylib -o makevis.so makevis.c

gcc -O3 -Wall -fPIC -shared -I/System/Library/Frameworks/Python.framework/Versions/2.7/include/python2.7 -L/opt/local/lib /opt/local/lib/libpython2.7.dylib -o makevis.so makevis.c

# gcc -O3 -Wall -fPIC -shared -I/sma/python/anaconda/pkgs/python-2.7.6-1/include/python2.7/ /sma/python/anaconda/pkgs/python-2.7.6-1/lib/libpython2.7.so -o makevis.so makevis.c


otool -L makevis.so

