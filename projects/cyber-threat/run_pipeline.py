# run_pipeline.py - simple runner that executes end-to-end steps
import os
os.system("python data_gen.py")
os.system("python preprocess.py --input data/synthetic_network.csv --outdir processed")
os.system("python train.py --processed processed --outdir models")
