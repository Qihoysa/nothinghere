import numpy as np
import simpleaudio as sa
import torch
import utils
from text.symbols import symbols
from text import cleaned_text_to_sequence
from vits_pinyin import VITS_PinYin
import cn2an


class Vits:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.ttf_front = VITS_PinYin("../bert", self.device)
        self.hps = utils.get_hparams_from_file("../configs/bert_vits.json")
        self.net_g = utils.load_class(self.hps.train.eval_class)(len(symbols),
                                                                 self.hps.data.filter_length // 2 + 1,
                                                                 self.hps.train.segment_size // self.hps.data.hop_length,
                                                                 **self.hps.model)
        utils.load_model("../vits_bert_model.pth", self.net_g)
        self.net_g.eval()
        self.net_g.to(self.device)

    def speaking(self, message):
        message = message.replace('-', '至').replace('~', "至")
        message = cn2an.transform(message + "了", 'an2cn')
        message = message.replace(" ", "").replace("\"", "").replace("\'", "")#('-', '负').replace('~', "至")
        print(message)
        phonemes, char_embeds = self.ttf_front.chinese_to_phonemes(message)
        input_ids = cleaned_text_to_sequence(phonemes)
        with torch.no_grad():
            x_tst = torch.LongTensor(input_ids).unsqueeze(0).to(self.device)
            x_tst_lengths = torch.LongTensor([len(input_ids)]).to(self.device)
            x_tst_prosody = torch.FloatTensor(char_embeds).unsqueeze(0).to(self.device)
            audio = self.net_g.infer(x_tst, x_tst_lengths, x_tst_prosody, noise_scale=0.5,
                                     length_scale=1.3)[0][0, 0].data.cpu().float().numpy()
        audio *= 32767 / np.max(np.abs(audio))
        audio = audio.astype(np.int16)
        play_obj = sa.play_buffer(audio, 1, 2, 22050)
        play_obj.wait_done()
