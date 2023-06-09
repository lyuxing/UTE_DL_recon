# Unet for qMRI
# 2020.10.18 Unet with 4 layers

import torch
import torch.nn as nn

def double_conv(in_channels, out_channels):
    return nn.Sequential(
        nn.Conv2d(in_channels, out_channels, 3, padding=1),
        nn.ReLU(inplace=True),
        nn.Conv2d(out_channels, out_channels, 3, padding=1),
        nn.ReLU(inplace=True)
    )   


class UNet(nn.Module):

    def __init__(self, n_input,n_class):
        super().__init__()
                
        self.dconv_down1 = double_conv(n_input, 64)
        self.dconv_down2 = double_conv(64, 128)
        self.dconv_down3 = double_conv(128, 256)
        self.dconv_down4 = double_conv(256, 512)
        self.dconv_down5 = double_conv(512, 512) # added
        # self.dconv_down6 = double_conv(512, 512) # added

        self.maxpool = nn.MaxPool2d(2)
        self.upsample = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)

        # self.dconv_up5 = double_conv(512 + 512, 512) #added
        self.dconv_up4 = double_conv(512 + 512, 512) #added
        self.dconv_up3 = double_conv(256 + 512, 256)
        self.dconv_up2 = double_conv(128 + 256, 128)
        self.dconv_up1 = double_conv(128 + 64, 64)
        
        self.conv_last = nn.Conv2d(64, n_class, 1)
        
        
    def forward(self, x):
        conv1 = self.dconv_down1(x)
        x = self.maxpool(conv1)

        conv2 = self.dconv_down2(x)
        x = self.maxpool(conv2)
        
        conv3 = self.dconv_down3(x)
        x = self.maxpool(conv3)   
        
        conv4 = self.dconv_down4(x)
        x = self.maxpool(conv4)

        # conv5 = self.dconv_down5(x)
        # x = self.maxpool(conv5)

        x = self.dconv_down5(x)

        x = self.upsample(x)        
        # x = torch.cat([x, conv5], dim=1)
        #
        # x = self.dconv_up5(x)
        # x = self.upsample(x)
        x = torch.cat([x, conv4], dim=1)

        x = self.dconv_up4(x)
        x = self.upsample(x)
        x = torch.cat([x, conv3], dim=1)

        x = self.dconv_up3(x)
        x = self.upsample(x)        
        x = torch.cat([x, conv2], dim=1)       

        x = self.dconv_up2(x)
        x = self.upsample(x)        
        x = torch.cat([x, conv1], dim=1)   
        
        x = self.dconv_up1(x)
        
        out = self.conv_last(x)
        
        return out


if __name__ == "__main__":

    num_classes = 5
    input_tensor = torch.autograd.Variable(torch.rand(6, 3, 224, 224)).cuda()
    # model = resnet50(class_num=num_classes)
    # model = UNet(n_channels=3,n_classes=num_classes,height=512,width=512).cuda()
    model = UNet(n_input=3,n_class=num_classes).cuda()
    output = model(input_tensor)

    print(output)