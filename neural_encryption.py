import tensorflow as tf
from datagen import get_key
from datagen import get_plain_text
import numpy as np

class Model:
    def __init__(self,bit_count,AB = True,training = True):
        '''
        Meant to hold onto the network object
        Arguments:
            bit_count: the length of the plain text
            AB: Whether or not you would like to create an Alice/Bob or Eve network
            training: if you want the weights to be trainable
        '''
        self.AB = AB
        self.name = 'Alice_Bob' if self.AB else 'Eve'
        self.input_length = 2*bit_count if AB else bit_count
        self.trainable = training
        self.input_layer = tf.placeholder(dtype = tf.float32, shape=(None,self.input_length,1))
        self.network = self.create_network()

    def create_network(self):

        
        #Create a 2N x 2N deep dense layer for Alice/Bob and N x 2N if Eve 
        self.dense_depth = self.input_length-1 if self.AB else (2*self.input_length)-1

        #Dense layers for mixing the plaintext
        self.dense_layers = tf.layers.dense(inputs=self.input_layer,
                                            units=self.input_length,
                                            trainable = self.trainable)

        for i in range(0,self.dense_depth):
            self.dense_layers = tf.layers.dense(inputs=self.dense_layers,
                                                units=self.input_length,
                                                trainable = self.trainable)

        #Four conv layers for transforming the ciphertext
        self.conv1 = tf.layers.conv1d(inputs=self.dense_layers,
                                    filters=2, 
                                    strides=[1],
                                    kernel_size = [4], 
                                    padding='same',
                                    activation=tf.sigmoid,
                                    trainable = self.trainable)
        self.conv2 = tf.layers.conv1d(inputs=self.conv1,
                                    filters=4, 
                                    strides=[2],
                                    kernel_size = [2], 
                                    padding='same',
                                    activation=tf.sigmoid,
                                    trainable = self.trainable)
        self.conv3 = tf.layers.conv1d(inputs=self.conv2,
                                    filters=4, 
                                    strides=[1],
                                    kernel_size = [1], 
                                    padding='same',
                                    activation=tf.sigmoid,
                                    trainable = self.trainable)
        self.conv4 = tf.layers.conv1d(inputs=self.conv3,
                                    filters=1, 
                                    strides=[1],
                                    kernel_size = [1], 
                                    padding='same',
                                    activation=tf.tanh,
                                    trainable = self.trainable)
        return self.conv4

def main():
    num_bits = 16
    batch = 1000

    print ('Generating plain text and key...')
    messages = get_plain_text(N=num_bits,to_generate=batch)
    AB_key = get_key(N=num_bits)

    m_with_key = [np.concatenate((AB_key[0],messages[i])) for i in range(batch)]

    #Inputs are [batch_size, image_width, image_height, channels]
    train_X = np.expand_dims(m_with_key,axis = 2) #prep for passing into network

    AB_net = Model(bit_count=num_bits,AB = True,training=True)
    E_net = Model(bit_count=num_bits,AB = False,training=True)

    with tf.Session() as sess:
        tf.global_variables_initializer().run()
        a = sess.run(AB_net.network, feed_dict={AB_net.input_layer: train_X})
        print (train_X.shape)
        print (a.shape)
        print (train_X[0])
        print (a[0])

if __name__ == "__main__":
    main()