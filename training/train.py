import os
import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from keras.applications import EfficientNetB0
from keras import layers, Model
import matplotlib.pyplot as plt

def build_model_fixed(input_shape=(224, 224, 3)):
    base_model = EfficientNetB0(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    
    base_model.trainable = True
    for layer in base_model.layers[:-30]: 
        layer.trainable = False
    
    inputs = layers.Input(shape=input_shape)
    x = base_model(inputs, training=True)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.4)(x)
    outputs = layers.Dense(1, activation='sigmoid')(x)
    
    model = Model(inputs, outputs)
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss='binary_crossentropy',
        metrics=['accuracy', 
                 tf.keras.metrics.Precision(name='precision'),
                 tf.keras.metrics.Recall(name='recall')]
    )
    
    return model

def train_model_fixed(train_dir='data/train', 
                      test_dir='data/test',
                      epochs=20,
                      batch_size=32):
    
    print("="*60)
    print("PIXELFORENSICS - FIXED MODEL TRAINING")
    print("="*60)
    
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,
        width_shift_range=0.3,
        height_shift_range=0.3,
        shear_range=0.2,
        zoom_range=0.3,
        horizontal_flip=True,
        brightness_range=[0.8, 1.2],
        fill_mode='nearest',
        validation_split=0.2 
    )
    
    test_datagen = ImageDataGenerator(rescale=1./255)
    
    print("\n📁 Loading training data...")
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='binary',
        shuffle=True,
        subset='training'
    )
    
    val_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='binary',
        shuffle=False,
        subset='validation'
    )
    
    print("\n📁 Loading test data...")
    test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='binary',
        shuffle=False
    )
    
    print(f"\n✓ Training samples: {train_generator.samples}")
    print(f"✓ Validation samples: {val_generator.samples}")
    print(f"✓ Test samples: {test_generator.samples}")
    
    print("\n🔨 Building improved model...")
    model = build_model_fixed()
    print(f"✓ Total parameters: {model.count_params():,}")
    
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            'models/best_model.h5',
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
            patience=8,
            restore_best_weights=True,
            verbose=1
        )
    ]
    
    print(f"\n🚀 Starting training for {epochs} epochs...")
    print("-"*60)
    
    history = model.fit(
        train_generator,
        epochs=epochs,
        validation_data=val_generator,
        callbacks=callbacks,
        verbose=1
    )
    
    model.save('models/final_model.h5')
    model.save('models/deepfake_detector.h5')
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].plot(history.history['accuracy'], label='Train')
    axes[0].plot(history.history['val_accuracy'], label='Validation')
    axes[0].set_title('Accuracy')
    axes[0].legend()
    axes[0].grid(True)
    
    axes[1].plot(history.history['loss'], label='Train')
    axes[1].plot(history.history['val_loss'], label='Validation')
    axes[1].set_title('Loss')
    axes[1].legend()
    axes[1].grid(True)
    
    plt.savefig('models/training_history.png')
    plt.close()
    
    print("\n📊 Final evaluation on test set...")
    results = model.evaluate(test_generator)
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    print(f"Test Accuracy:  {results[1]*100:.2f}%")
    print(f"Test Precision: {results[2]*100:.2f}%")
    print(f"Test Recall:    {results[3]*100:.2f}%")
    print("="*60)
    
    return model, history

if __name__ == "__main__":
    model, history = train_model_fixed(
        train_dir='data/train',
        test_dir='data/test',
        epochs=20,
        batch_size=32
    )