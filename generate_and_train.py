"""
generate_and_train.py
─────────────────────────────────────────────────────────────────────────────
Phase 2: AI Model Integration — ContractGuard
─────────────────────────────────────────────────────────────────────────────

Run this ONCE on your local machine. It will:
  1. Generate 80 synthetic document images per class (320 total)
  2. Train a MobileNetV2 transfer-learning classifier
  3. Save  model/keras_model.h5  and  model/labels.txt

Usage:
    pip install tensorflow Pillow numpy
    python generate_and_train.py

Takes ~5 minutes on CPU.  After it finishes, push the model/ folder to GitHub
and your Streamlit Cloud app will automatically use it.
"""

import os, random, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ── Config ────────────────────────────────────────────────────────────────────
CLASSES        = ["Rental Agreement", "Employment Contract", "Terms of Service", "Other"]
N_PER_CLASS    = 80          # synthetic images per class
IMG_SIZE       = 224         # Teachable Machine default
EPOCHS         = 15
BATCH_SIZE     = 16
TRAIN_SPLIT    = 0.8
DATA_DIR       = "synthetic_data"
MODEL_DIR      = "model"
SEED           = 42
random.seed(SEED);  np.random.seed(SEED)

os.makedirs(MODEL_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# PART 1 — Synthetic image generator
# Each class has a distinct visual signature so the model can learn easily.
# ─────────────────────────────────────────────────────────────────────────────

def rand_color(base, spread=25):
    """Jitter a base RGB tuple so every image is slightly different."""
    return tuple(max(0, min(255, c + random.randint(-spread, spread))) for c in base)

def draw_text_lines(draw, x, y, width, n_lines, line_h=9, color=(80,80,80), alpha_jitter=True):
    """Draw paragraph-like horizontal lines simulating text."""
    for i in range(n_lines):
        line_width = int(width * random.uniform(0.55, 0.97))
        c = rand_color(color, 20) if alpha_jitter else color
        draw.rectangle([x, y, x + line_width, y + line_h - 2], fill=c)
        y += line_h + random.randint(2, 5)
    return y

def generate_rental_agreement(idx):
    """Blue header, landlord/tenant table, stamp circles, signature line."""
    img = Image.new("RGB", (IMG_SIZE, IMG_SIZE), rand_color((245,245,250), 8))
    d = ImageDraw.Draw(img)

    # Header bar — blue
    hh = random.randint(28, 40)
    d.rectangle([0, 0, IMG_SIZE, hh], fill=rand_color((30, 60, 180), 20))
    # White title lines in header
    d.rectangle([10, 8, random.randint(100,160), 16], fill=(220,230,255))
    d.rectangle([10, 19, random.randint(60,100), 24], fill=(180,200,240))

    y = hh + 10
    # Two column layout (landlord | tenant)
    col = IMG_SIZE // 2 - 5
    for _ in range(random.randint(3, 5)):
        w = random.randint(35, 60)
        d.rectangle([8, y, 8+w, y+8], fill=rand_color((100,120,200), 15))
        d.rectangle([col+5, y, col+5+w, y+8], fill=rand_color((100,120,200), 15))
        lw = random.randint(50, 85)
        d.rectangle([8+w+4, y, 8+w+4+lw, y+8], fill=rand_color((160,160,160), 20))
        d.rectangle([col+5+w+4, y, col+5+w+4+lw, y+8], fill=rand_color((160,160,160), 20))
        y += 14

    # Divider
    d.rectangle([0, y+4, IMG_SIZE, y+6], fill=rand_color((30,60,180),20))
    y += 14

    # Body text lines
    y = draw_text_lines(d, 8, y, IMG_SIZE-16, random.randint(6,10))
    y += 6
    # Clause block
    d.rectangle([4, y, 8, y+40], fill=rand_color((30,60,180),20))
    y = draw_text_lines(d, 14, y, IMG_SIZE-22, random.randint(3,5))
    y += 8

    # Stamp circles (bottom right)
    for _ in range(random.randint(1,2)):
        cx = random.randint(150, IMG_SIZE-20)
        # FIX: Ensure the lower bound never exceeds the upper bound (IMG_SIZE-16)
        cy_start = min(max(y, IMG_SIZE-60), IMG_SIZE-16)
        cy = random.randint(cy_start, IMG_SIZE-15)
        r  = random.randint(16, 28)
        d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=rand_color((30,60,180),15), width=2)
        d.ellipse([cx-r+4, cy-r+4, cx+r-4, cy+r-4], outline=rand_color((30,60,180),15), width=1)

    # Signature line
    sx = random.randint(8, 20)
    # FIX: Ensure the lower bound never exceeds the upper bound (IMG_SIZE-11)
    sy_start = min(max(y+4, IMG_SIZE-22), IMG_SIZE-11)
    sy = random.randint(sy_start, IMG_SIZE-10)
    d.rectangle([sx, sy, sx + random.randint(60,100), sy+1], fill=(80,80,80))

    return img

def generate_employment_contract(idx):
    """Green/teal header, letterhead style, bullet points, signature box at bottom."""
    img = Image.new("RGB", (IMG_SIZE, IMG_SIZE), rand_color((250,250,248), 6))
    d = ImageDraw.Draw(img)

    # Letterhead top — green accent bar (left side)
    d.rectangle([0, 0, 6, IMG_SIZE], fill=rand_color((20,140,80), 25))

    # Company logo placeholder (top right)
    lx, ly = IMG_SIZE-45, 8
    d.rectangle([lx, ly, lx+38, ly+22], fill=rand_color((20,140,80),20), outline=rand_color((20,140,80),10), width=1)

    # Title block
    y = 10
    d.rectangle([14, y, 14+random.randint(100,150), y+10], fill=rand_color((20,140,80),20))
    y += 14
    d.rectangle([14, y, 14+random.randint(60,90), y+7], fill=rand_color((100,100,100),20))
    y += 16

    # Divider
    d.rectangle([14, y, IMG_SIZE-10, y+1], fill=rand_color((20,140,80),20))
    y += 8

    # Intro paragraph
    y = draw_text_lines(d, 14, y, IMG_SIZE-28, random.randint(3,5))
    y += 6

    # Bullet points (4–7 items)
    for _ in range(random.randint(4, 7)):
        bx, by = 14, y
        d.ellipse([bx, by+1, bx+6, by+7], fill=rand_color((20,140,80),20))
        line_w = random.randint(80, IMG_SIZE-40)
        d.rectangle([bx+10, by+2, bx+10+line_w, by+8], fill=rand_color((120,120,120),20))
        y += 13

    y += 4
    # Another paragraph
    y = draw_text_lines(d, 14, y, IMG_SIZE-28, random.randint(2,4))
    y += 8

    # Signature box (bottom)
    bh = random.randint(28, 40)
    by_box = max(y+4, IMG_SIZE - bh - 8)
    d.rectangle([14, by_box, 14+85, by_box+bh],
                outline=rand_color((20,140,80),20), width=1)
    d.rectangle([14+10, by_box+bh-10, 14+75, by_box+bh-9], fill=(120,120,120))

    return img

def generate_terms_of_service(idx):
    """Dark red/purple header, numbered sections, dense text, checkbox row."""
    img = Image.new("RGB", (IMG_SIZE, IMG_SIZE), rand_color((252,251,255), 5))
    d = ImageDraw.Draw(img)

    # Full-width header — dark red/purple
    hh = random.randint(32, 45)
    hc = rand_color((120, 20, 160), 25)
    d.rectangle([0, 0, IMG_SIZE, hh], fill=hc)
    # Title lines in header
    d.rectangle([8, 8, 8+random.randint(110,170), 17], fill=(230,210,255))
    d.rectangle([8, 20, 8+random.randint(60,100), 27], fill=(200,180,240))

    y = hh + 8
    # Intro text
    y = draw_text_lines(d, 8, y, IMG_SIZE-16, random.randint(2,3), color=(80,80,80))
    y += 6

    # Numbered sections (3-5)
    for sec in range(random.randint(3, 5)):
        # Section heading
        d.rectangle([8, y, 8+random.randint(5,8), y+9], fill=hc)
        d.rectangle([18, y, 18+random.randint(70,120), y+9], fill=rand_color((60,20,90),20))
        y += 13
        # Section body
        y = draw_text_lines(d, 14, y, IMG_SIZE-22, random.randint(2,4), color=(100,100,100))
        y += 4

    # Checkbox row (bottom area)
    if y < IMG_SIZE - 30:
        for _ in range(random.randint(2, 4)):
            if y >= IMG_SIZE - 14: break
            d.rectangle([8, y+1, 16, y+9], outline=(100,100,100), width=1)
            if random.random() > 0.4:
                d.line([9,y+2,15,y+8], fill=(80,80,80), width=1)
            line_w = random.randint(60, IMG_SIZE-30)
            d.rectangle([20, y+3, 20+line_w, y+7], fill=rand_color((120,120,120),20))
            y += 14

    # Footer line
    d.rectangle([0, IMG_SIZE-12, IMG_SIZE, IMG_SIZE-11], fill=hc)
    d.rectangle([8, IMG_SIZE-9, 8+random.randint(80,160), IMG_SIZE-5], fill=rand_color((150,100,180),20))

    return img

def generate_other(idx):
    """Non-document: colorful noise, geometric shapes, no text structure."""
    img = Image.new("RGB", (IMG_SIZE, IMG_SIZE), rand_color((200,200,200),40))
    d = ImageDraw.Draw(img)

    # Random background color
    bg = (random.randint(60,220), random.randint(60,220), random.randint(60,220))
    img.paste(Image.new("RGB", (IMG_SIZE, IMG_SIZE), bg))
    d = ImageDraw.Draw(img)

    # Random geometric shapes
    for _ in range(random.randint(5, 15)):
        shape_type = random.randint(0, 2)
        x1, y1 = random.randint(0,IMG_SIZE-20), random.randint(0,IMG_SIZE-20)
        x2, y2 = x1+random.randint(10,80), y1+random.randint(10,80)
        c = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        if shape_type == 0:
            d.rectangle([x1,y1,x2,y2], fill=c)
        elif shape_type == 1:
            d.ellipse([x1,y1,x2,y2], fill=c)
        else:
            points = [(random.randint(0,IMG_SIZE), random.randint(0,IMG_SIZE)) for _ in range(4)]
            d.polygon(points, fill=c)

    # Add some noise pixels
    pixels = img.load()
    for _ in range(random.randint(200, 600)):
        px = random.randint(0, IMG_SIZE-1)
        py = random.randint(0, IMG_SIZE-1)
        pixels[px, py] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))

    return img

GENERATORS = {
    "Rental Agreement":    generate_rental_agreement,
    "Employment Contract": generate_employment_contract,
    "Terms of Service":    generate_terms_of_service,
    "Other":               generate_other,
}

# ── Generate all images ───────────────────────────────────────────────────────
print("\n── STEP 1: Generating synthetic training images ──────────────────────")
for cls in CLASSES:
    folder = os.path.join(DATA_DIR, cls.replace(" ", "_").replace("/", "_"))
    os.makedirs(folder, exist_ok=True)
    gen = GENERATORS[cls]
    for i in range(N_PER_CLASS):
        img = gen(i)
        img.save(os.path.join(folder, f"{i:04d}.png"))
    print(f"  ✓ {cls}: {N_PER_CLASS} images saved → {folder}")

print(f"\n  Total: {N_PER_CLASS * len(CLASSES)} images across {len(CLASSES)} classes")

# ── Save labels.txt ───────────────────────────────────────────────────────────
with open(os.path.join(MODEL_DIR, "labels.txt"), "w") as f:
    for i, cls in enumerate(CLASSES):
        f.write(f"{i} {cls}\n")
print(f"\n  ✓ labels.txt saved → {MODEL_DIR}/labels.txt")

# ─────────────────────────────────────────────────────────────────────────────
# PART 2 — Train with TensorFlow / Keras (MobileNetV2 transfer learning)
# Same architecture that Teachable Machine uses internally.
# ─────────────────────────────────────────────────────────────────────────────
print("\n── STEP 2: Training MobileNetV2 classifier ───────────────────────────")
print("  Loading TensorFlow… (first import may take ~30 seconds)")

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping

tf.random.set_seed(SEED)
print(f"  TensorFlow version: {tf.__version__}")

# Data pipeline with augmentation
datagen = ImageDataGenerator(
    rescale=1./127.5,
    preprocessing_function=lambda x: x - 1.0,   # normalize to [-1, 1]
    rotation_range=8,
    width_shift_range=0.08,
    height_shift_range=0.08,
    zoom_range=0.08,
    horizontal_flip=False,
    validation_split=1 - TRAIN_SPLIT,
)

train_gen = datagen.flow_from_directory(
    DATA_DIR, target_size=(IMG_SIZE, IMG_SIZE), batch_size=BATCH_SIZE,
    class_mode="categorical", subset="training", seed=SEED,
)
val_gen = datagen.flow_from_directory(
    DATA_DIR, target_size=(IMG_SIZE, IMG_SIZE), batch_size=BATCH_SIZE,
    class_mode="categorical", subset="validation", seed=SEED,
)

# Verify class order matches CLASSES list
print(f"\n  Class indices from generator: {train_gen.class_indices}")
# Re-write labels.txt to match generator's order
with open(os.path.join(MODEL_DIR, "labels.txt"), "w") as f:
    for cls_name, idx in sorted(train_gen.class_indices.items(), key=lambda x: x[1]):
        display_name = cls_name.replace("_", " ")
        f.write(f"{idx} {display_name}\n")

# Build model: frozen MobileNetV2 base + trainable head
# Try to load imagenet weights (much better accuracy). Falls back to random if offline.
try:
    print("  Downloading MobileNetV2 ImageNet weights (~14MB)…")
    base = MobileNetV2(input_shape=(IMG_SIZE, IMG_SIZE, 3), include_top=False, weights="imagenet")
    print("  ✓ ImageNet weights loaded — expect 90%+ accuracy")
except Exception:
    print("  ⚠ No internet — using random weights (still trains, just needs more epochs)")
    base = MobileNetV2(input_shape=(IMG_SIZE, IMG_SIZE, 3), include_top=False, weights=None)
base.trainable = False

model = models.Sequential([
    base,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation="relu"),
    layers.Dropout(0.3),
    layers.Dense(len(CLASSES), activation="softmax"),
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

model.summary()

early_stop = EarlyStopping(monitor="val_accuracy", patience=4, restore_best_weights=True)

print(f"\n  Training for up to {EPOCHS} epochs…")
history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS,
    callbacks=[early_stop],
    verbose=1,
)

# Save in Keras format (same as Teachable Machine export)
model_path = os.path.join(MODEL_DIR, "keras_model.h5")
model.save(model_path)

print(f"\n── STEP 3: Done ─────────────────────────────────────────────────────")
print(f"  ✓ Model saved  → {model_path}")
print(f"  ✓ Labels saved → {MODEL_DIR}/labels.txt")

val_loss, val_acc = model.evaluate(val_gen, verbose=0)
print(f"\n  Final validation accuracy: {val_acc*100:.1f}%")
print(f"\n  Next steps:")
print(f"  1. git add model/  &&  git commit -m 'feat: add trained classifier'  &&  git push")
print(f"  2. Streamlit Cloud will auto-redeploy with the model")
print(f"  3. Go to Upload File tab → upload a document image → see the classifier in action")
