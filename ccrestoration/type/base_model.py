import sys
from abc import ABC, abstractmethod
from typing import Any, Optional

import torch

from ccrestoration.utils.device import DEFAULT_DEVICE


class BaseModelInterface(ABC):
    """
    Base model interface

    :param config: config of the model
    :param device: inference device
    :param fp16: use fp16 or not
    :param compile: use torch.compile or not
    :param compile_backend: backend of torch.compile
    """

    def __init__(
        self,
        config: Any,
        device: Optional[torch.device] = None,
        fp16: bool = True,
        compile: bool = False,
        compile_backend: Optional[str] = None,
    ) -> None:
        self.config = config
        self.device: Optional[torch.device] = device
        self.fp16: bool = fp16
        self.compile: bool = compile
        self.compile_backend: Optional[str] = compile_backend

        if device is None:
            self.device = DEFAULT_DEVICE

        self.model: torch.nn.Module = self.load_model()

        # fp16
        if self.fp16:
            try:
                self.model = self.model.half()
            except Exception as e:
                print(f"Error: {e}, fp16 is not supported on this model.")
                self.fp16 = False
                self.model = self.load_model()

        # compile
        if self.compile:
            try:
                if self.compile_backend is None:
                    if sys.platform == "darwin":
                        self.compile_backend = "aot_eager"
                    else:
                        self.compile_backend = "inductor"
                self.model = torch.compile(self.model, backend=self.compile_backend)
            except Exception as e:
                print(f"Error: {e}, compile is not supported on this model.")

    def get_state_dict(self) -> Any:
        raise NotImplementedError

    def load_model(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    @torch.inference_mode()  # type: ignore
    def inference(self, img: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError

    @torch.inference_mode()  # type: ignore
    def inference_video(self, clip: Any) -> Any:
        """
        Inference the video with the model, the clip should be a vapoursynth clip

        :param clip: vs.VideoNode
        :return:
        """
        raise NotImplementedError

    def __call__(self, img: torch.Tensor) -> torch.Tensor:
        return self.inference(img)