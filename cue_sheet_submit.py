import pydub
import requests

# Reference: https://app.swaggerhub.com/apis-docs/Socan7/Cue_Sheet_Hackathon/1.0.0#/cue%20sheet/post%20v1%20catalog%20av%20work

api_key = ""


def submit_cue_sheet(data):
    url = "https://api.socan.ca/sandbox/v1/catalog/av-work"
    response = requests.post(url, json=data, params={"apiKey": api_key})
    print(response.status_code)
    print(response.text)


def main():
    segment = pydub.AudioSegment.from_ogg("dataset/example.ogg")
    av_category_code = "F"
    av_work_cues = [
        {
            "workTitle": "Example",
            "cueUsageCode": "B",
            "duration": 32,
            "cueIps": [
                {
                    "ipName": "Example Inc",
                    "ipFunction": "W",
                }
            ]
        }
    ]
    av_work_duration = len(segment) / 1000
    av_work_title = "CueConnect"
    production_year = 2022
    data = {
        "avCategoryCode": av_category_code,
        "avWorkCues": av_work_cues,
        "avWorkDuration": av_work_duration,
        "avWorkTitle": av_work_title,
        "productionYear": production_year,
    }
    submit_cue_sheet(data)


if __name__ == "__main__":
    main()
