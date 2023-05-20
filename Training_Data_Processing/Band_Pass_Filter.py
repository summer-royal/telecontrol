import argparse
import time
import brainflow
import numpy as np

import pandas as pd
import matplotlib
import os

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, NoiseTypes

from google.colab import drive
drive.mount('/content/drive')

from google.colab import files
%matplotlib inline

def main():
    #BoardShim.enable_dev_board_logger()

    # use cyton board 
    params = BrainFlowInputParams()
    board_id = BoardIds.CYTON_BOARD.value
    board = BoardShim(board_id, params)
    
    for filename in os.listdir('/content/drive/My Drive/Testing Data'):
      
      # get data from file
      restored_data = DataFilter.read_file('/content/drive/My Drive/Testing Data/' + str(filename))
      restored_df = pd.DataFrame(np.transpose(restored_data))
      # print('Data From the File')
      # print(restored_df.head(10))

      # demo how to convert it to pandas DF and plot data
      eeg_channels = BoardShim.get_eeg_channels(board_id)
      # df = pd.DataFrame(np.transpose(restored_data))
      # plt.figure()
      # df[eeg_channels].plot(subplots=True)
      # plt.savefig('before_processing.png')

      # for demo apply different filters to different channels, in production choose one
      for channel in eeg_channels:
        DataFilter.perform_bandpass(restored_data[channel], BoardShim.get_sampling_rate(board_id), 65.0, 35.0, 4,
                                          FilterTypes.BESSEL.value, 0)
        

    
      DataFilter.write_file(restored_data, "/content/drive/My Drive/Testing Data/" + filename, 'w')  # use 'a' for append mode
      # df = pd.DataFrame(np.transpose(restored_data))
      # plt.figure()
      # df[eeg_channels].plot(subplots=True)
    
      # plt.show()
      # plt.savefig('after_processing.png')
    
  


if __name__ == "__main__":
    main()
