import numpy as np
from scipy import signal
import warnings; warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt

Listx_pdm = []
file1 = open(r"/home/pi/sampledata.txt","r")

def create_tuplex_pdm():
    for x in range(1537): 
        bytebuffer = file1.read(2)
        decimal = int(bytebuffer,16)
        Listx_pdm.append(decimal)
    return(tuple(Listx_pdm))

Tx_pdm = create_tuplex_pdm()
file1.close()

oversample_rate = 64
def quantize(x,b,x_range):
    n_steps = 2**b
    delta = (x_range[1]-x_range[0])/n_steps
    bins = np.arange(x_range[0],x_range[1], delta)
    return np.digitize(x, bins) - (len(bins)/2 + 1),bins

def pdm_to_pcm(pdm,oversample_rate, b):
    pcm = signal.decimate(pdm,oversample_rate, zero_phase=True, ftype='fir',n=80)
    pcm,_ = quantize(pcm,b,(-1,1))
    return pcm

reconstructed_pcm = pdm_to_pcm(Tx_pdm, oversample_rate, 16)
plt.ioff()
fig = plt.plot(reconstructed_pcm)
plt.title("PCM signal converted from PDM")
plt.xlabel('Samples')
plt.ylabel('Amplitude (16-bit)')
plt.savefig("katietest2.png")

