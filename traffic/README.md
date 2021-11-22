#Experimentation Process

At first, i started out simple, trying a single convolutional layer,
one pooling layer, a hidden dense layer with 100 nodes and the output layer.
This first run i didn't use any dropout layer, which is why i think i suffered
from overfitting (0.6 less accuracy on testing than on training data)

I decided to add some dropout (0.5) which improved the overfitting problem but the
accuracy wasn't very high. I started researching on how to select the ideal amount
of layers, and the ideal amount of nodes in them. I added a few more convolutional layers,
a first one learning 64 filters, second one 32, and third one 16.
On top of that I decided to change the nodes in the hidden dense layer from 100 
(which was just an arbitrary selection i did) to the mean between 2 values: 
the amount of pixels in the images (input), and the number of categories (output).

This changes led to a pretty good accuracy on training and testing data.