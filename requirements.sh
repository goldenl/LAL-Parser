# PyTorch with CUDA 12.1 support (compatible with CUDA 12.2)
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu121

# Core dependencies
pip install cython==3.0.0
pip install numpy==1.24.3
pip install sentencepiece==0.1.99

# Ubuntu 20.04 HDF5 support (use either apt package or pip wheel)
sudo apt-get update
sudo apt-get install -y libhdf5-dev
pip install h5py==3.9.0

# TensorFlow (for compatibility, optional if not strictly needed)
pip install tensorflow==2.13.0

# Transformers (modern version that maintains backward compatibility)
pip install transformers==4.30.0

# TensorBoard
pip install tensorboard==2.13.0
pip install tensorboardX==2.6

# NLP tools
pip install nltk==3.8.1

# Progress bars
pip install tqdm==4.65.0

# Benepar for parsing
pip install benepar[gpu]==0.2.0

# Download NLTK data
python3 -m nltk.downloader punkt averaged_perceptron_tagger

# Download pre-trained model
pip install gdown
gdown https://drive.google.com/uc?id=1LC5iVcvgksQhNVJ-CbMigqXnPAaquiA2

# If you get a "Too many users have viewed or downloaded this file recently." error, 
# run the following 3 lines to download pre-trained model from a mirror:
# pip install internetarchive
# ia download neuraladobe-ucsdparser
# mv neuraladobe-ucsdparser/best_parser.pt .
