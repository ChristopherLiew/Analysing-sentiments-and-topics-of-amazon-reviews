import os
import time
import pickle
import pandas as pd
from ast import literal_eval
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import multilabel_confusion_matrix, classification_report
from gensim import models
from tensorflow.keras import utils
from tensorflow import data

def get_clf_results(y_true, y_pred):
    print(multilabel_confusion_matrix(y_true, y_pred))
    return pd.DataFrame(classification_report(y_true, y_pred, output_dict=True))

def tune_model(model, X, search_params, verbosity=True, n_jobs=-1):
    tuner = RandomizedSearchCV(
        model, search_params, verbose=verbosity, n_jobs=n_jobs)
    train_data, train_labels = X
    search = tuner.fit(train_data, train_labels)
    return search.best_estimator_, search.best_score_, search.best_params_

def save_model(model, filepath):
    with open(filepath, 'wb') as file:
        pickle.dump(model, file)
        print('Model successfully saved at: ' + filepath)

def load_model(filepath):
    with open(filepath, 'rb') as file:
        print('Loading model from: ' + filepath)
        return pickle.load(file)

def convert_to_lists(string_data):
    '''
    Use when converting back from csv data.
    '''
    return [literal_eval(i) for i in string_data]

def create_bigrams(text, min_count=20):
    sleep(0.1)
    # Higher min_words and threshold-> Harder to form bigrams
    bigram = models.Phrases(text, min_count)
    bigram_mod = models.phrases.Phraser(
        bigram)  # Creates a memory efficient model of phrases w/o model state (Ok if we do not need to train on new docs)
    return [bigram_mod[doc] for doc in text]  # Transform doc to bigrams

def create_trigrams(bigrams, min_count=5):
    trigram = models.Phrases(bigrams, min_count)
    trigram_mod = models.phrases.Phraser(trigram)
    return [trigram_mod[doc] for doc in bigrams]

def create_tf_ds(X, y=None, shuffle=True):
    if y:
        # convert labels into one_hot_encoded labels
        y = utils.to_categorical(y)
        ds = data.Dataset.from_tensor_slices((X, y))
        if shuffle:
            # Buffer Size = Size of DS for perfect shuffling
            return ds.shuffle(len(ds))
        return ds
    else:
        ds = data.Dataset.from_tensor_slices(X)
        if shuffle:
            return ds.shuffle((len(ds)))
        return ds

def get_log_dir():
    root_log_dir = os.path.join(os.curdir, "Transformer Models/my_logs")
    run_id = time.strftime("run_%Y_%m_%d-%H_%M_%S")
    return os.path.join(root_log_dir, run_id)
