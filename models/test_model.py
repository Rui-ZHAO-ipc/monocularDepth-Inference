import numpy as np
import torch
import os
from collections import OrderedDict
from torch.autograd import Variable
import itertools
import util.util as util
from util.image_pool import ImagePool
from .base_model import BaseModel
from . import networks
import sys

class TestModel(BaseModel):
    def name(self):
        return 'TestModel'
    def initialize(self, args):
        BaseModel.initialize(self, args)
        self.input_A = self.Tensor(1, 3, 1024, 256)

        self.netG_AtoB = networks.define_G(3, 3, 64, 'resnet_9blocks', 'instance', False, args.init_type, self.gpu_ids)
        self.netG_BtoC = networks.define_G(3, 4, 64, 'unet_256', 'batch', False, args.init_type, self.gpu_ids)

        checkpoint_AtoB_filename = 'netG_A2B.pth'
        checkpoint_BtoC_filename = 'netG_B2C.pth'

        checkpoint_path_AtoB = os.path.join(args.checkpoints_dir, checkpoint_AtoB_filename)
        checkpoint_path_BtoC = os.path.join(args.checkpoints_dir, checkpoint_BtoC_filename)

        self.netG_AtoB.load_state_dict(torch.load(checkpoint_path_AtoB))
        self.netG_BtoC.load_state_dict(torch.load(checkpoint_path_BtoC))

        print('---------- Networks initialized -------------')
        networks.print_network(self.netG_AtoB)
        networks.print_network(self.netG_BtoC)
        print('-----------------------------------------------')

    def set_input(self, input):
        # we need to use single_dataset mode
        input_A = input['A']
        self.input_A.resize_(input_A.size()).copy_(input_A)
        self.image_paths = input['A_paths']

    def test(self):
        self.real_A = Variable(self.input_A)
        self.fake_B = self.netG_AtoB(self.real_A)
        self.fake_C = self.netG_BtoC(self.fake_B)


    # get image paths
    def get_image_paths(self):
        return self.image_paths

    def get_current_visuals(self):
        real_A = util.tensor2im(self.real_A.data)
        fake_B = util.tensor2im(self.fake_B.data)
        fake_C = util.tensor2im(self.fake_C.data)

        return OrderedDict([('real_A', real_A), ('fake_B', fake_B), ('fake_C', fake_C)])