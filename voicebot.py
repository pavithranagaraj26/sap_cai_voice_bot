import telegram
from telegram.ext import Updater,MessageHandler,Filters,CommandHandler
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import logging
from cai import CAI
import os

logging.basicConfig(level=logging.INFO)

config = {
    'API_KEY':os.environ['API_KEY'],
    'id':[int(os.environ['id'])],
}

LANG_ID = "en"#"ru"# 
if LANG_ID=='ru':
    MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-russian"
else:
    MODEL_ID = "facebook/wav2vec2-base-960h"
processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)

def get_preds(OUTFILE):
    resampler = torchaudio.transforms.Resample(48_000, 16_000)

    def speech_file_to_array_fn(batch):
        speech_array, sampling_rate = torchaudio.load(batch)
        batch = resampler(speech_array).squeeze().numpy()
        return batch

    test_dataset = speech_file_to_array_fn(OUTFILE)

    inputs = processor(test_dataset, sampling_rate=16_000, return_tensors="pt", padding=True)

    with torch.no_grad():
        if LANG_ID=='ru':
            logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits
        else:
            logits = model(inputs.input_values).logits
    
    predicted_ids = torch.argmax(logits, dim=-1)
    return processor.batch_decode(predicted_ids)

c = CAI()

def voice_handler(update, context):
    file_handler = context.bot.getFile(update.message.voice.file_id)
    file = file_handler.download('./voice.ogg')
    try:
        text = get_preds(file)[0]
        logging.info(f'The text - {text}')
        cai_resp = c.get_response(text)
        for i in cai_resp:
            if i['type']=='text':
                update.message.reply_text(i['content'])
    except:
        update.message.reply_text('Sorry!')

def text_handler(update, context):
    cai_resp = c.get_response(update.message.text)
    for i in cai_resp:
        if i['type']=='text':
            update.message.reply_text(i['content'])

def help_command(update, context):
    update.message.reply_text('Help!')

def main() -> None:
    """Run the bot."""
    logging.info('Ready!')
    # Create the Updater and pass it your bot's token.
    updater = Updater(config['API_KEY'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(MessageHandler(Filters.voice, voice_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, text_handler))

    dispatcher.add_handler(CommandHandler("help", help_command))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
