# Page-summarizer

GPT-2 page summarizer
This model is built to be able to summarize a page using the GPT-2 model which is a new breed of text-generation systems that have impressed experts with their ability to generate coherent text from minimal prompts. The system was trained on eight million text documents scraped from the web and responds to text snippets supplied by users.

Well in actuality the API is meant to be deployed and ready to use by consumers but challanges have been faced in deployment because of the large size of the model so a true test cannot be provided, work is still being carried out on the deployment.

# Api documentation
Home directory ("/") for full documentaion

Post Request to "/summarizer" using {"text": text_to_be_sumarized} which returns {"msg":summarized_text}
