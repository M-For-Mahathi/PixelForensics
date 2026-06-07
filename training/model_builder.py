import tensorflow as tf
import tensorflow
from keras import layers, Model
from keras.applications import MobileNetV2

def build_deepfake_detector(input_shape=(224, 224, 3), trainable_layers=20):
    
    base_model = MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    
    for layer in base_model.layers[:-trainable_layers]:
        layer.trainable = False
    
    for layer in base_model.layers[-trainable_layers:]:
        layer.trainable = True
    
    inputs = layers.Input(shape=input_shape)
    
    x = base_model(inputs, training=True)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    
    outputs = layers.Dense(1, activation='sigmoid', name='output')(x)
    model = Model(inputs=inputs, outputs=outputs, name='PixelForensics_Detector')
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss='binary_crossentropy',
        metrics=[
            'accuracy',
            tf.keras.metrics.Precision(name='precision'),
            tf.keras.metrics.Recall(name='recall')
        ]
    )
    
    print("✓ Model built successfully")
    print(f"✓ Total parameters: {model.count_params():,}")
    print(f"✓ Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")
    
    return model


def get_callbacks(model_save_path='models/best_model.h5'):
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=model_save_path,
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1
        ),
        
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=7,
            restore_best_weights=True,
            verbose=1
        )
    ]
    
    return callbacks