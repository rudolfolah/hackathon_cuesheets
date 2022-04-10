1. Train the machine learning model to recognize songs and pieces of songs within other works: `python machine_learning_model.py`
2. Process a work by uploading to S3 and then using the Dolby IO API to analyze it: `python main.py`, the job ids for analysis tasks are stored in `dolby_job_ids.txt`
3. After this the work is ready to be submitted as a cue sheet to SOCAN: `python cue_sheet_submit.py`
