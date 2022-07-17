import PyPDF2
from tkinter import *
from tkinter import filedialog, messagebox
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir


file_path = ""


def open_file():
    global file_path
    filename = filedialog.askopenfilename(initialdir='/', title="Select a file", filetypes=[('Text Files',
                                                                                             '*pdf')])
    file_path = filename


def convert_audio():
    with open(file_path, 'rb') as pdfFileObj:
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        information = pdfReader.getDocumentInfo()
        number_of_pages = pdfReader.getNumPages()
        total_page = ""
        for page in range(number_of_pages):
            pageObj = pdfReader.getPage(page)
            page_to_read = pageObj.extractText()
            total_page += f"\n{page_to_read}"

    # Getting title as the name of the speech is there is a title
    try:
        title = information.title
    except AttributeError:
        title = "new_audio"

    session = Session(aws_access_key_id=os.environ.get("aws_access_key_id"),
                      aws_secret_access_key=os.environ.get("aws_secret_access_key"),
                      region_name="us-east-1")
    polly = session.client("polly")

    try:
        # Request speech synthesis
        response = polly.synthesize_speech(Text=total_page, OutputFormat="mp3",
                                           VoiceId="Joanna")
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)

    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
        with closing(response["AudioStream"]) as stream:
            output = os.path.join("/Users/Temitope/PycharmProjects/pdf-to-audio", f'{title}.mp3')

            try:
                # Open a file for writing the output as a binary stream
                with open(output, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                sys.exit(-1)
            else:
                messagebox.showinfo(title="Conversion Successful",
                                    message=f"Your pdf file has successfully been converted and it was saved as "
                                            f"{title}")

    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)

    # Play the audio using the platform's default player
    # Uncomment the lines below to play the audio
    # if sys.platform == "win32":
    #     os.startfile(output)
    # else:
    #     # The following works on macOS and Linux. (Darwin = mac, xdg-open = linux).
    #     opener = "open" if sys.platform == "darwin" else "xdg-open"
    #     subprocess.call([opener, output])

# -------------------------------------------- UI ------------------------------------------------#


window = Tk()
window.title("Image Watermarking Application")
window.minsize(width=500, height=300)
window.config(padx=50, pady=50)

header_label = Label(window,
                     text="Tunji's PDF to Audio File Converter",
                     width=60)
header_label.grid(column=1, row=1)

button_explore = Button(window,
                        text="Select File",
                        command=open_file)
button_explore.grid(column=1, row=2)

button_exit = Button(window,
                     text="Exit",
                     command=exit)
button_exit.grid(column=1, row=3)

convert_audio_button = Button(window, text="CONVERT PDF TO AUDIO", command=convert_audio, width=30)
convert_audio_button.grid(column=1, row=3)


window.mainloop()
