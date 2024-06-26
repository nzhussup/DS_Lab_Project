from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, GlobalMaxPool1D, Reshape, Bidirectional, Conv1D, MaxPooling1D, Flatten
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping
import tensorflow as tf
from sklearn.model_selection import train_test_split


class RNN:
    
    def __init__(self):
        self.max_words = 10000
        self.max_len = 500 # Actual max_len == 1766 but we use 500 because of the comp costs
        self.embedding = None
        self.num_classes = 4
        self.X_train = None
        self.X_test = None
        self.X_val = None
        self.y_train = None
        self.y_test = None
        self.y_val = None
        self.train_seq = None
        self.test_seq = None
        self.val_seq = None
        
    def tokenize(self, train, test, val=None):
        
        self.X_train, self.X_test = train['text'], test['text']
        self.y_train, self.y_test = train['label_ids'], test['label_ids']
        
        tokenizer = Tokenizer(num_words=self.max_words)
        tokenizer.fit_on_texts(self.X_train)
        self.train_seq = tokenizer.texts_to_sequences(self.X_train)
        self.test_seq = tokenizer.texts_to_sequences(self.X_test)
        
        if val is not None and not val.empty:
            self.X_val, self.y_val = val['text'], val['label_ids']
            self.val_seq = tokenizer.texts_to_sequences(self.X_val)
            
        print("Attributes updated, use <self.train_seq> etc. to use values")
    
    def pad_and_label_preproc(self):
        
        X_train = pad_sequences(self.train_seq, maxlen = self.max_len)
        y_train = tf.keras.utils.to_categorical(self.y_train, self.num_classes)
        X_test = pad_sequences(self.test_seq, maxlen = self.max_len)
        y_test = tf.keras.utils.to_categorical(self.y_test, self.num_classes)
        
        if self.val_seq != None:
            X_val = pad_sequences(self.val_seq, maxlen=self.max_len)
            y_val = tf.keras.utils.to_categorical(self.y_val, self.num_classes)
            return  X_train, X_test, X_val, y_train, y_test, y_val
        
        return X_train, X_test, y_train, y_test
    
    def build_model(self, use_basic_embed: bool, reshape=50, optimizer = "adam"):
        
        if use_basic_embed:
            
            model = Sequential()
            # KERAS 3 version model.add(Embedding(input_dim = self.max_words, output_dim = 200, input_shape = (self.max_len, )))
            model.add(Embedding(input_dim = self.max_words, output_dim = 200, input_length = self.max_len, ))
            print("Using basic embedding")
            model.add(Bidirectional(LSTM(128, return_sequences=True)))
            model.add(Dropout(0.5))
            model.add(GlobalMaxPool1D())
            model.add(Dropout(0.4))
            model.add(Dense(256, activation='relu'))
            model.add(Dropout(0.4))
            model.add(Dense(128, activation='relu'))
            model.add(Dropout(0.4))
            model.add(Dense(self.num_classes, activation='softmax'))
            model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
            
        else:
            model = Sequential()
            
            model.add(self.embedding)
            model.add(Reshape((1, reshape)))

            model.add(Bidirectional(LSTM(128, return_sequences=True)))
            model.add(Dropout(0.5))
            model.add(GlobalMaxPool1D())
            model.add(Dropout(0.4))
            model.add(Dense(256, activation='relu'))
            model.add(Dropout(0.4))
            model.add(Dense(128, activation='relu'))
            model.add(Dropout(0.4))
            model.add(Dense(self.num_classes, activation='softmax'))
            model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

        print(model.summary())
        
        early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
        
        return model, early_stop
    



class CNN(RNN):
    
    def __init__(self):
        
        super().__init__()
        self.filters = 16
        self.kernel_size = 3
        
    def tokenize(self, train, test, val=None):
        
        self.X_train, self.X_test = train['text'], test['text']
        self.y_train, self.y_test = train['label_ids'], test['label_ids']
        
        tokenizer = Tokenizer(num_words=self.max_words)
        tokenizer.fit_on_texts(self.X_train)
        self.train_seq = tokenizer.texts_to_sequences(self.X_train)
        self.test_seq = tokenizer.texts_to_sequences(self.X_test)
        
        if val is not None and not val.empty:
            self.X_val, self.y_val = val['text'], val['label_ids']
            self.val_seq = tokenizer.texts_to_sequences(self.X_val)
            
        print("Attributes updated, use <self.train_seq> etc. to use values")
    
    def pad_and_label_preproc(self):
        
        X_train = pad_sequences(self.train_seq, maxlen = self.max_len)
        y_train = tf.keras.utils.to_categorical(self.y_train, self.num_classes)
        X_test = pad_sequences(self.test_seq, maxlen = self.max_len)
        y_test = tf.keras.utils.to_categorical(self.y_test, self.num_classes)
        
        if self.val_seq != None:
            X_val = pad_sequences(self.val_seq, maxlen=self.max_len)
            y_val = tf.keras.utils.to_categorical(self.y_val, self.num_classes)
            return  X_train, X_test, X_val, y_train, y_test, y_val
        
        return X_train, X_test, y_train, y_test
    
    def build_model(self, use_basic_embed: bool, reshape=50, add_globalmaxpool=False, optimizer="adam"):
        
        if use_basic_embed:
            
            model = Sequential()
            # KERAS 3 version model.add(Embedding(input_dim = self.max_words, output_dim = 200, input_shape = (self.max_len, )))
            model.add(Embedding(input_dim = self.max_words, output_dim = 200, input_length = self.max_len, ))
            print("Using basic embedding")
            model.add(Dropout(0.5))
            
            model.add(Conv1D(128, self.kernel_size, padding='same', activation='relu'))
            model.add(MaxPooling1D())
            
            model.add(Conv1D(64, self.kernel_size, padding='same', activation='relu'))
            model.add(MaxPooling1D())
            
            model.add(Conv1D(32, self.kernel_size, padding='same', activation='relu'))
            model.add(MaxPooling1D())
            
            model.add(Flatten())
            
            model.add(Dense(256, activation='relu'))
            model.add(Dropout(0.5))

            model.add(Dense(self.num_classes, activation='softmax'))
            model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
            
        else:
            model = Sequential()
            # KERAS 3 version model.add(Embedding(input_dim = self.max_words, output_dim = 200, input_shape = (self.max_len, )))
            model.add(self.embedding)
            model.add(Reshape((1, reshape)))
            print("Using custom embedding")
            model.add(Dropout(0.3))
            
            model.add(Conv1D(128, self.kernel_size, padding='same', activation='relu'))
            model.add(Conv1D(64, self.kernel_size, padding='same', activation='relu'))
            model.add(Conv1D(32, self.kernel_size, padding='same', activation='relu'))
            
            if add_globalmaxpool:
                model.add(GlobalMaxPool1D())
            
            model.add(Flatten())
            
            model.add(Dense(256, activation='relu'))
            model.add(Dropout(0.3))

            model.add(Dense(self.num_classes, activation='softmax'))
            model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

        print(model.summary())
        
        early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
        
        return model, early_stop

