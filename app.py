# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hKSDUwzMc4txj7o56TsDn8-Tyv1X8Qgz
"""

import json
import os
import numpy as np
import tensorflow as tf
import model, sample, encoder
from flask import Flask, request
from flask_restplus import Api, Resource

app = Flask(__name__)
api =  Api(app, version='1.0', title='Text Summarizer', description='A summarizer for text, articles, blog posts etc')

namespace = api.namespace('', description='Main API Routes')


def interact_model(model_name,seed,nsamples,batch_size,length,temperature,top_k,models_dir,article):
    result_list = []
    models_dir = os.path.expanduser(os.path.expandvars(models_dir))
    if batch_size is None:
        batch_size = 1
    assert nsamples % batch_size == 0

    enc = encoder.get_encoder(model_name, models_dir)
    hparams = model.default_hparams()
    with open(os.path.join(models_dir, model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))

    if length is None:
        length = hparams.n_ctx // 2
    elif length > hparams.n_ctx:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

    with tf.Session(graph=tf.Graph()) as sess:
        context = tf.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
            temperature=temperature, top_k=top_k
        )

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join(models_dir, model_name))
        saver.restore(sess, ckpt)

        # while True:
        raw_text = article+"\n TF;DR:"
        while not raw_text:
            return 'Text should not be empty!'
            # raw_text = input("Model prompt >>> ")
        context_tokens = enc.encode(raw_text)
        generated = 0
        for i in range(3):
            for _ in range(nsamples // batch_size):
                out = sess.run(output, feed_dict={
                    context: [context_tokens for _ in range(batch_size)]
                })[:, len(context_tokens):]
                for i in range(batch_size):
                    generated += 1
                    text = enc.decode(out[i])
                    result_list.append(str(text))
        result_list.append(str(raw_text))
        result_list = pd.Series(result_list)
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(result_list)
        cosine_sim = linear_kernel(tfidf_matrix)
        sim_scores = list(enumerate(cosine_sim[3]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1]
        return result_list[sim_scores[0]].split("<|endoftext|>")[0]

@namespace.route("/summarizer")
class Summary(Resource):
  @namespace.doc(description='takes text and returns summary')
  def post(self):
    article = request.form.get('text')
    if article == None:
        return {"msg":"invalid request"}, 400
    result = interact_model(
      '774M',
      None,
      1,
      1,
      100,
      0.5,
      0,
      './models',
      article
  )
    return {"msg":result}, 200

if __name__ == "__main__":
    app.run(debug=True)

# import threading
# threading.Thread(target=app.run, kwargs={'host':'0.0.0.0','port':80}).start()

# import requests
# r = requests.post("http://172.28.0.2/summarizer", {"text":'''Let's define habits. Habits are the small decisions you make and actions you perform every day. According to researchers at Duke University, habits account for about 40 percent of our behaviors on any given day. 

# Your life today is essentially the sum of your habits. How in shape or out of shape you are? A result of your habits. How happy or unhappy you are? A result of your habits. How successful or unsuccessful you are? A result of your habits.

# What you repeatedly do (i.e. what you spend time thinking about and doing each day) ultimately forms the person you are, the things you believe, and the personality that you portray. Everything I write about – from procrastination and productivity to strength and nutrition – starts with better habits. When you learn to transform your habits, you can transform your life.'''})
# print(r.status_code)
# print(r.encoding)
# print(r.apparent_encoding)
# print(r.text)