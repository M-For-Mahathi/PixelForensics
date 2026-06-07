# organize_dataset.py
import os
import shutil
from pathlib import Path

print("="*60)
print("ORGANIZING DATASET")
print("="*60)

source_real = "real_vs_fake/real-vs-fake/train/real"
source_fake = "real_vs_fake/real-vs-fake/train/fake"

alt_source_real = "real_vs_fake/real-vs-fake/test/real"
alt_source_fake = "real_vs_fake/real-vs-fake/test/fake"

if not os.path.exists(source_real):
    if os.path.exists("real_vs_fake/train/real"):
        source_real = "real_vs_fake/train/real"
        source_fake = "real_vs_fake/train/fake"
    elif os.path.exists("real-vs-fake/train/real"):
        source_real = "real-vs-fake/train/real"
        source_fake = "real-vs-fake/train/fake"
    else:
        print(f"❌ ERROR: Cannot find source folders")
        print("Please check the extracted folder structure")
        print("\nLooking for folders at:")
        print(f"  - {source_real}")
        print(f"  - real_vs_fake/train/real")
        print(f"  - real-vs-fake/train/real")
        exit()

print(f"✓ Found source folders:")
print(f"  Real: {source_real}")
print(f"  Fake: {source_fake}")

print("\n📂 Scanning images...")
real_images = list(Path(source_real).glob("*.jpg")) + list(Path(source_real).glob("*.png"))
fake_images = list(Path(source_fake).glob("*.jpg")) + list(Path(source_fake).glob("*.png"))

if os.path.exists(alt_source_real):
    real_images += list(Path(alt_source_real).glob("*.jpg")) + list(Path(alt_source_real).glob("*.png"))
    fake_images += list(Path(alt_source_fake).glob("*.jpg")) + list(Path(alt_source_fake).glob("*.png"))

print(f"✓ Found {len(real_images)} real images")
print(f"✓ Found {len(fake_images)} fake images")

if len(real_images) == 0 or len(fake_images) == 0:
    print("\n❌ ERROR: No images found!")
    print("Please check the folder structure manually.")
    exit()

train_real_count = min(4000, len(real_images) - 500)
test_real_count = min(500, len(real_images) - train_real_count)
train_fake_count = min(4000, len(fake_images) - 500)
test_fake_count = min(500, len(fake_images) - train_fake_count)

print(f"\n📊 Will organize:")
print(f"  Training: {train_real_count} real + {train_fake_count} fake")
print(f"  Testing:  {test_real_count} real + {test_fake_count} fake")

os.makedirs("data/train/real", exist_ok=True)
os.makedirs("data/train/fake", exist_ok=True)
os.makedirs("data/test/real", exist_ok=True)
os.makedirs("data/test/fake", exist_ok=True)

print("\n📦 Copying images to data folders...")
print("This may take a few minutes...\n")

print(f"Copying {train_real_count} real images to training set...")
for i, img in enumerate(real_images[:train_real_count]):
    dest = f"data/train/real/{img.name}"
    shutil.copy(str(img), dest)
    if (i + 1) % 500 == 0:
        print(f"  ✓ Copied {i + 1}/{train_real_count}")

print(f"✓ Training real images copied")

print(f"Copying {test_real_count} real images to test set...")
for i, img in enumerate(real_images[train_real_count:train_real_count + test_real_count]):
    dest = f"data/test/real/{img.name}"
    shutil.copy(str(img), dest)

print(f"✓ Test real images copied")

print(f"\nCopying {train_fake_count} fake images to training set...")
for i, img in enumerate(fake_images[:train_fake_count]):
    dest = f"data/train/fake/{img.name}"
    shutil.copy(str(img), dest)
    if (i + 1) % 500 == 0:
        print(f"  ✓ Copied {i + 1}/{train_fake_count}")

print(f"✓ Training fake images copied")

print(f"Copying {test_fake_count} fake images to test set...")
for i, img in enumerate(fake_images[train_fake_count:train_fake_count + test_fake_count]):
    dest = f"data/test/fake/{img.name}"
    shutil.copy(str(img), dest)

print(f"✓ Test fake images copied")

print("\n" + "="*60)
print("✅ DATASET ORGANIZED SUCCESSFULLY!")
print("="*60)
print(f"Training set:")
print(f"  - Real: {len(os.listdir('data/train/real'))} images")
print(f"  - Fake: {len(os.listdir('data/train/fake'))} images")
print(f"\nTest set:")
print(f"  - Real: {len(os.listdir('data/test/real'))} images")
print(f"  - Fake: {len(os.listdir('data/test/fake'))} images")
print("="*60)
print("\n✅ Next step: Create all Python files in preprocessing/, training/, utils/")
print("Then run: python training/train.py")
print("="*60)