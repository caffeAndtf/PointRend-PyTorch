from collections import OrderedDict

from torchvision.models._utils import IntermediateLayerGetter
from torchvision.models.utils import load_state_dict_from_url
from torchvision.models.resnet import resnet50, resnet101
from torchvision.models.segmentation._utils import _SimpleSegmentationModel
from torchvision.models.segmentation.deeplabv3 import DeepLabHead
from torchvision.models.segmentation.fcn import FCNHead
from .resnet import resnet103


class SmallDeepLab(_SimpleSegmentationModel):
    def forward(self, input_):
        result = self.backbone(input_)
        result["coarse"] = self.classifier(result["out"])

        if False: # self.aux_classifier is not None:
            x = self.aux_classifier(result["aux"])
            # x = F.interpolate(x, size=input_shape, mode='bilinear', align_corners=False)
            result["aux"] = x
        return result


def deeplabv3(pretrained=False, resnet="res103", head_in_ch=2048, num_classes=21):
    resnet = {
        "res101": resnet101,
        "res103": resnet103
    }[resnet]

    net = SmallDeepLab(
        backbone=IntermediateLayerGetter(
            resnet103(pretrained=True, replace_stride_with_dilation=[False, True, True]),
            return_layers={'layer2': 'res2', 'layer4': 'out'}
        ),
        classifier=DeepLabHead(head_in_ch,      num_classes),
        aux_classifier=FCNHead(head_in_ch // 2, num_classes)
    )
    if pretrained:
        state_dict = load_state_dict_from_url('https://download.pytorch.org/models/deeplabv3_resnet101_coco-586e9e4e.pth', progress=True)
        net.load_state_dict(state_dict)
    return net


if __name__ == "__main__":
    import torch
    x = torch.randn(3, 3, 512, 1024).cuda()
    net = deeplabv3(False).cuda()
    result = net(x)
    for k, v in result.items():
        print(k, v.shape)
