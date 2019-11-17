from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import pathlib
from PIL import Image
from azure.cognitiveservices.vision.computervision.models import TextOperationStatusCodes
import time
from azure.cognitiveservices.vision.computervision.models import TextOperationStatusCodes
import time
import cv2
import os

def create_client():
    endpoint = '[your cognitive service protal endpoint here]'
    key = '[your key here]'

    credentials = CognitiveServicesCredentials(key)
    client = ComputerVisionClient(endpoint, credentials)
    return client

def search_text(text, video_file_path):
    cap = cv2.VideoCapture(video_file_path)
    ret, image = cap.read()
    
    seconds = 1
    fps = cap.get(cv2.CAP_PROP_FPS) #Returns frames per second

    multiplier = fps * seconds

    temp_path = "temp-frame.jpg"
    if not os.path.exists("images"):
        os.makedirs("images")

    while ret:
        frameID = int(round(cap.get(1))) #current frame number
        ret, image1 = cap.read()
        temp_frameID = frameID/fps
        if frameID % multiplier == 0:
            cv2.imwrite(temp_path, image1)
            image = open(temp_path, 'rb')
            raw = True
            custom_headers = None
            numberOfCharsInOperationId = 36

            # Async SDK call
            rawHttpResponse = client.batch_read_file_in_stream(image, custom_headers,  raw)

            # Get ID from returned headers
            operationLocation = rawHttpResponse.headers["Operation-Location"]
            idLocation = len(operationLocation) - numberOfCharsInOperationId
            operationId = operationLocation[idLocation:]

            while True:
                result = client.get_read_operation_result(operationId)
                if result.status not in ['NotStarted', 'Running']:
                    break
                time.sleep(0.1)

            if result.status == TextOperationStatusCodes.succeeded:
                for textResult in result.recognition_results:
                    for line in textResult.lines:
                        print(line.text)
                        # print(line.bounding_box)
                        if text in line.text:
                            print("Text found: "+line.text)
                            value = temp_frameID
                            minutes = int(value/60)
                            seconds = int(((value/60) - minutes)*60)
                            print(str(minutes)+":"+str(seconds))
                            cv2.imwrite("images/frame%d.jpg" %temp_frameID, image1)

    
    
    cap.release()





if __name__ == '__main__':

    client = create_client()

    video_path = "[path to your video]"
    text_to_search = "[text to search]"

    search_text(text_to_search, video_path)