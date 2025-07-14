# Download
wget -nc https://ftp.gnu.org/gnu/grep/grep-3.11.tar.gz

# Decompress
tar -xzvf grep-3.11.tar.gz

# Compile and build
cd grep-3.11
mkdir -p obj-temp && cd obj-temp
make distclean
../configure --disable-shared --prefix=$PWD
make