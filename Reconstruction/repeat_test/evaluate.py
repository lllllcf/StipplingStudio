import argparse
from torch.utils.data import Dataset, DataLoader
import torch

import torch.nn as nn
from torchvision import models
from torch.nn.functional import relu

import cv2
import glob


class StipplingReconstructionCNN(nn.Module):
    def __init__(self, n_class):
        super().__init__()

        # Encoder
        # In the encoder, convolutional layers with the Conv2d function are used to extract features from the input image.
        # Each block in the encoder consists of two convolutional layers followed by a max-pooling layer, with the exception of the last block which does not include a max-pooling layer.
        # -------
        # input: 800x600x1
        self.e11 = nn.Conv2d(1, 64, kernel_size=3, padding=1) # output: 798x766x64
        self.e12 = nn.Conv2d(64, 64, kernel_size=3, padding=1) # output: 796x764x64
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2) # output: 398x382x64

        # input: 510x382x64
        self.e21 = nn.Conv2d(64, 128, kernel_size=3, padding=1) # output: 508x380x128
        self.e22 = nn.Conv2d(128, 128, kernel_size=3, padding=1) # output: 394x378x128
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2) # output: 197x189x128

        # input: 253x189x128
        self.e31 = nn.Conv2d(128, 256, kernel_size=3, padding=1) # output: 251x138x256
        self.e32 = nn.Conv2d(256, 256, kernel_size=3, padding=1) # output: 193x136x256
        self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2) # output: 97x68x256

        # input: 68x68x256
        self.e41 = nn.Conv2d(256, 512, kernel_size=3, padding=1) # output: 66x66x512
        self.e42 = nn.Conv2d(512, 512, kernel_size=3, padding=1) # output: 93x64x512
        self.pool4 = nn.MaxPool2d(kernel_size=2, stride=2, ceil_mode=True) # output: 32x32x512

        # input: 32x32x512
        self.e51 = nn.Conv2d(512, 1024, kernel_size=3, padding=1) # output: 30x30x1024
        self.e52 = nn.Conv2d(1024, 1024, kernel_size=3, padding=1) # output: 28x28x1024


        # Decoder
        self.upconv1 = nn.ConvTranspose2d(1024, 512, kernel_size=2, stride=2)
        self.d11 = nn.Conv2d(1024, 512, kernel_size=3, padding=1)
        self.d12 = nn.Conv2d(512, 512, kernel_size=3, padding=1)

        self.upconv2 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.d21 = nn.Conv2d(512, 256, kernel_size=3, padding=1)
        self.d22 = nn.Conv2d(256, 256, kernel_size=3, padding=1)

        self.upconv3 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.d31 = nn.Conv2d(256, 128, kernel_size=3, padding=1)
        self.d32 = nn.Conv2d(128, 128, kernel_size=3, padding=1)
        self.upconv4 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.d41 = nn.Conv2d(128, 64, kernel_size=3, padding=1)
        self.d42 = nn.Conv2d(64, 64, kernel_size=3, padding=1)

        # self.median_blur = MedianBlur(kernel_size=5)
        # self.bilateral_filter = BilateralFilter(d=5, sigmaColor=0.5, sigmaSpace=2.0)

        # Output layer
        self.outconv = nn.Conv2d(64, n_class, kernel_size=1)

    def forward(self, x):
        # Encoder
        # print(x.size())
        xe11 = relu(self.e11(x))
        # print(xe11.size())
        xe12 = relu(self.e12(xe11))
        # print(xe12.size())
        xp1 = self.pool1(xe12)
        # print(xp1.size())

        xe21 = relu(self.e21(xp1))
        # print(xe21.size())
        xe22 = relu(self.e22(xe21))
        # print(xe22.size())
        xp2 = self.pool2(xe22)
        # print(xp2.size())

        xe31 = relu(self.e31(xp2))
        # print(xe31.size())
        xe32 = relu(self.e32(xe31))
        # print(xe32.size())
        xp3 = self.pool3(xe32)
        # print(xp3.size())

        xe41 = relu(self.e41(xp3))
        # print(xe41.size())
        xe42 = relu(self.e42(xe41))
        # print(xe42.size())
        xp4 = self.pool4(xe42)
        # print(xp4.size())

        xe51 = relu(self.e51(xp4))
        # print(xe51.size())
        xe52 = relu(self.e52(xe51))
        # print(xe52.size())

        # Decoder
        xu1 = self.upconv1(xe52)
        # print(xu1.size())
        xu11 = torch.cat([xu1, xe42], dim=1)
        # print(xu11.size())
        xd11 = relu(self.d11(xu11))
        # print(xd11.size())
        xd12 = relu(self.d12(xd11))
        # print(xd12.size())

        xu2 = self.upconv2(xd12)
        xu22 = torch.cat([xu2, xe32], dim=1)
        xd21 = relu(self.d21(xu22))
        xd22 = relu(self.d22(xd21))

        xu3 = self.upconv3(xd22)
        xu33 = torch.cat([xu3, xe22], dim=1)
        xd31 = relu(self.d31(xu33))
        xd32 = relu(self.d32(xd31))

        xu4 = self.upconv4(xd32)
        xu44 = torch.cat([xu4, xe12], dim=1)
        xd41 = relu(self.d41(xu44))
        xd42 = relu(self.d42(xd41))



        # Output layer
        out = self.outconv(xd42)
        print(out.size())

        # out = self.median_blur(out)
        # out = self.bilateral_filter(out)

        return out
    
index = 50
stippling_img_path = "./data/s" + str(index) + ".png"
reconstruction_img_path = "./data/r" + str(index) + ".png"
stippling_img = torch.FloatTensor(cv2.resize(cv2.imread(stippling_img_path, cv2.IMREAD_GRAYSCALE), (800, 592))).unsqueeze(0) / 255.0

best_model = StipplingReconstructionCNN(1)
checkpoint = torch.load("../checkpoints/final.pth.tar", map_location=torch.device('cpu'))
best_model.load_state_dict(checkpoint["state_dict"])

best_model.eval()
reconstructed_img = best_model(stippling_img.unsqueeze(1))
cv2.imwrite(reconstruction_img_path, reconstructed_img[0].squeeze().detach().numpy() * 255.0)