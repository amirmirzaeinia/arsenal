# Arsenal: Understanding AI-driven Congestion Control Protocols via In-depth Evaluation
## Overview

![images](https://github.com/arsenalcc2019/arsenal/blob/master/images/overview.png)


This work is the first to make an extensive comparative study of all mainstream AI-driven congestion control algorithms, under a custom-designed uniform evaluation platform. The system architecture consists of following modules:


+ **Video telephony module** is an adaptive real-time video communication system, which transmits video content according to the instantaneous network available bandwidth estimated by the underlying CC algorithms. Arsenal faithfully emulates real-world video telephony by implementing the video codec, frame formulation and packet parsing components.
+ **Bulk file transfer.** For a comprehensive evaluation, Arsenal designs a bulk file transfer module to examine the performance of transmitting non-video content. Different from video telephony, file transfer supports full-throttle and continuous traffic.
+ **CC algorithms collection:** Arsenal incorporates a series of representative AI-driven transport algorithms, as shown in Table. 1: 2 traditional machine learning (i.e., ML, not based on deep neural network) based algorithms (Remy, PCC-Vivace) and 4 deep learning (DL) based algorithms (Pensieve’V, Aurora, Concerto and Indigo). Besides, we also use two widely used non-AI protocols, BBR and WebRTC. 
+ **Link simulator.** Arsenal collects and uses large-scale video-telephony traces with ≥ 1 million sessions and the 1-second fine-grained records, from a mainstream live-video APP in China. Arsenal then designs a trace mapping procedure that allows the link emulation software mahimahi to faithfully simulate the practical network dynamics.
+ **Video and file analysis.** Arsenal develops an analysis module at receiver side to record and calculate the performance metrics for evaluating different CC algorithms.

![images](https://github.com/arsenalcc2019/arsenal/blob/master/images/algorithms.png)
