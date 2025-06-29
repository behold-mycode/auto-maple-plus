import os
import platform
import numpy as np

# Platform-specific imports and implementations
if platform.system() == "Windows":
	import ctypes.wintypes
	
	dll_path = os.path.join(os.path.dirname(__file__), "gdi_capture.dll")
	gdi_capture_dll = ctypes.WinDLL(dll_path)

	gdi_capture_dll.FindWindowFromExecutableName.restype = ctypes.wintypes.HWND
	gdi_capture_dll.FindWindowFromExecutableName.argtype = [ctypes.wintypes.LPCWSTR]

	gdi_capture_dll.CaptureWindow.restype = ctypes.wintypes.HBITMAP
	gdi_capture_dll.CaptureWindow.argtype = [ctypes.wintypes.HWND, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.POINTER(ctypes.c_uint8))]

	gdi_capture_dll.FreeBitmapHandle.restype = None
	gdi_capture_dll.FreeBitmapHandle.argtype = [ctypes.wintypes.HBITMAP]

	def find_window_from_executable_name(name):
		return gdi_capture_dll.FindWindowFromExecutableName(name)

	class CaptureWindow:
		def __init__(self, hwnd):
			self.hwnd = hwnd

		def __enter__(self):
			width = ctypes.c_long()
			height = ctypes.c_long()
			bitmap_ptr = ctypes.POINTER(ctypes.c_uint8)()

			self.bitmap_handle = gdi_capture_dll.CaptureWindow(self.hwnd, ctypes.byref(width), ctypes.byref(height), ctypes.byref(bitmap_ptr))
			if self.bitmap_handle is None:
				return

			return np.ctypeslib.as_array(bitmap_ptr, shape=(height.value, width.value, 4))

		def __exit__(self, exc_type, exc_value, traceback):
			if self.bitmap_handle is None:
				return

			gdi_capture_dll.FreeBitmapHandle(ctypes.wintypes.HBITMAP(self.bitmap_handle))

else:
	# Non-Windows platforms (macOS, Linux)
	# Use alternative screen capture methods
	
	def find_window_from_executable_name(name):
		"""
		Cross-platform window finding.
		On non-Windows platforms, return a placeholder or use alternative methods.
		"""
		print(f"[INFO] Window finding not implemented for {platform.system()}, using fallback")
		return None

	class CaptureWindow:
		"""
		Cross-platform screen capture using alternative methods.
		"""
		def __init__(self, hwnd=None):
			self.hwnd = hwnd
			self.bitmap_handle = None

		def __enter__(self):
			"""
			Capture screen using platform-appropriate method.
			"""
			try:
				import mss
				with mss.mss() as sct:
					# Capture the entire screen as fallback
					screenshot = sct.grab(sct.monitors[1])  # Primary monitor
					# Convert to numpy array
					img_array = np.array(screenshot)
					# Convert from BGRA to RGBA if needed
					if img_array.shape[2] == 4:
						img_array = img_array[:, :, [2, 1, 0, 3]]  # BGRA to RGBA
					return img_array
			except Exception as e:
				print(f"[WARN] Screen capture failed: {e}")
				# Return a dummy array as fallback
				return np.zeros((100, 100, 4), dtype=np.uint8)

		def __exit__(self, exc_type, exc_value, traceback):
			"""
			Cleanup for cross-platform capture.
			"""
			pass
