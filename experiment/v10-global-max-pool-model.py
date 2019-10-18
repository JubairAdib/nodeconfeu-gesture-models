
import tensorflow as tf
import tensorflow.keras as keras

from nodeconfeu_watch.reader import AccelerationReader
from nodeconfeu_watch.visual import plot_history, classification_report
from nodeconfeu_watch.convert import ExportModel

tf.random.set_seed(1)

dataset = AccelerationReader('./data/gestures-v2', test_ratio=0.2, validation_ratio=0.2,
                              classnames=['swiperight', 'swipeleft', 'upup', 'waggle', 'clap2'])

model = keras.Sequential()
model.add(keras.Input(shape=(50, 1, 4), name='acceleration', dtype=dataset.train.x.dtype))
model.add(keras.layers.Conv2D(14, (5, 1), padding='valid', activation='relu'))
model.add(keras.layers.Dropout(0.2))
model.add(keras.layers.Conv2D(len(dataset.classnames), (5, 1), padding='same', dilation_rate=2, activation='relu'))
model.add(keras.layers.Dropout(0.1))
model.add(keras.layers.MaxPool2D((46, 1)))
model.add(keras.layers.Flatten())
model.add(keras.layers.Dense(len(dataset.classnames), use_bias=False))

model.compile(optimizer=keras.optimizers.Adam(),
              loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=[keras.metrics.SparseCategoricalAccuracy()])

history = model.fit(dataset.train.x, dataset.train.y,
                    batch_size=64,
                    epochs=500,
                    validation_data=(dataset.validation.x, dataset.validation.y))

print('')
print('Raw model performance on validation dataset')
print(classification_report(model, dataset, subset='validation'))

exporter = ExportModel(model, dataset, quantize=False)
print('')
print('Not-quantized model performance on test dataset')
print(classification_report(model, dataset, subset='test'))

print('')
print(exporter.size_report())
exporter.save('exports/v10.noquant.tflite')

exporter = ExportModel(model, dataset, quantize=True)
print('')
print('Quantized model performance on test dataset')
print(classification_report(model, dataset, subset='test'))

print('')
print(exporter.size_report())
exporter.save('exports/v10.quant.tflite')

plot_history(history)
