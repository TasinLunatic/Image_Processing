import cv2
import numpy as np
import matplotlib.pyplot as plt

# ========== 1. Load images ==========
OriI = cv2.imread('Chirose.jpg')
SecI = cv2.imread('your_second_image.jpg')   # change the name

if OriI is None:
    print("Error: Chirose.jpg not found!")
if SecI is None:
    print("Error: Second image not found!")

# Make them the same size
SecI = cv2.resize(SecI, (OriI.shape[1], OriI.shape[0]))

# ========== 2. Channel Swap ==========
rgb = cv2.cvtColor(OriI, cv2.COLOR_BGR2RGB)
b, g, r = cv2.split(OriI)
swapped = cv2.merge([g, r, b])

# ========== 3. Three Grayscale methods ==========
gray1 = cv2.cvtColor(OriI, cv2.COLOR_BGR2GRAY)                 # OpenCV
b, g, r = cv2.split(OriI.astype(np.float32))
gray2 = ((r + g + b) / 3).astype(np.uint8)                     # Average
gray3 = (0.299*r + 0.587*g + 0.114*b).astype(np.uint8)         # Weighted

# ========== 4. Rotation & Scaling ==========
h, w = OriI.shape[:2]
M = cv2.getRotationMatrix2D((w//2, h//2), 45, 1.0)

rotated_nearest = cv2.warpAffine(OriI, M, (w, h), flags=cv2.INTER_NEAREST)
rotated_linear  = cv2.warpAffine(OriI, M, (w, h), flags=cv2.INTER_LINEAR)
rotated_cubic   = cv2.warpAffine(OriI, M, (w, h), flags=cv2.INTER_CUBIC)

scaled = cv2.resize(OriI, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)

# ========== 5. Algebraic operations ==========
add = cv2.add(OriI, SecI)
sub = cv2.subtract(OriI, SecI)
mul = cv2.multiply(OriI.astype(np.float32)/255, SecI.astype(np.float32)/255)
mul = (mul * 255).astype(np.uint8)

# ========== 6. Change yellow rose color + gray background ==========
hsv = cv2.cvtColor(OriI, cv2.COLOR_BGR2HSV)
lower_yellow = np.array([20, 80, 80])
upper_yellow = np.array([35, 255, 255])
mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

hsv_changed = hsv.copy()
hsv_changed[mask > 0, 0] = 150          # change to purple/magenta (try 0 for red, 100 for blue...)
colored = cv2.cvtColor(hsv_changed, cv2.COLOR_HSV2BGR)

gray = cv2.cvtColor(OriI, cv2.COLOR_BGR2GRAY)
gray_3ch = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
result = np.where(mask[:, :, np.newaxis] > 0, colored, gray_3ch)

# ========== Display results ==========
plt.figure(figsize=(15, 10))

plt.subplot(3, 4, 1); plt.imshow(cv2.cvtColor(OriI, cv2.COLOR_BGR2RGB)); plt.title('Original'); plt.axis('off')
plt.subplot(3, 4, 2); plt.imshow(cv2.cvtColor(swapped, cv2.COLOR_BGR2RGB)); plt.title('Channel Swap'); plt.axis('off')
plt.subplot(3, 4, 3); plt.imshow(gray1, cmap='gray'); plt.title('Gray - OpenCV'); plt.axis('off')
plt.subplot(3, 4, 4); plt.imshow(gray3, cmap='gray'); plt.title('Gray - Weighted'); plt.axis('off')

plt.subplot(3, 4, 5); plt.imshow(cv2.cvtColor(rotated_linear, cv2.COLOR_BGR2RGB)); plt.title('Rotate 45° Linear'); plt.axis('off')
plt.subplot(3, 4, 6); plt.imshow(cv2.cvtColor(rotated_cubic, cv2.COLOR_BGR2RGB)); plt.title('Rotate 45° Cubic'); plt.axis('off')
plt.subplot(3, 4, 7); plt.imshow(cv2.cvtColor(add, cv2.COLOR_BGR2RGB)); plt.title('Addition'); plt.axis('off')
plt.subplot(3, 4, 8); plt.imshow(cv2.cvtColor(sub, cv2.COLOR_BGR2RGB)); plt.title('Subtraction'); plt.axis('off')

plt.subplot(3, 4, 9); plt.imshow(cv2.cvtColor(mul, cv2.COLOR_BGR2RGB)); plt.title('Multiplication'); plt.axis('off')
plt.subplot(3, 4, 10); plt.imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB)); plt.title('Yellow→New Color + Gray BG'); plt.axis('off')

plt.tight_layout()
plt.show()