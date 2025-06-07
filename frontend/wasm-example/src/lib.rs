use wasm_bindgen::prelude::*;

// When the `wee_alloc` feature is enabled, use `wee_alloc` as the global
// allocator.
#[cfg(feature = "wee_alloc")]
#[global_allocator]
static ALLOC: wee_alloc::WeeAlloc = wee_alloc::WeeAlloc::INIT;

#[wasm_bindgen]
extern "C" {
    // Use `js_namespace` here to bind `console.log(..)` instead of just
    // `log(..)`
    #[wasm_bindgen(js_namespace = console)]
    fn log(s: &str);
}

// A macro to provide `println!(..)`-style syntax for `console.log` logging.
macro_rules! console_log {
    ($($t:tt)*) => (log(&format!($($t)*)))
}

#[wasm_bindgen]
pub fn add(a: i32, b: i32) -> i32 {
    console_log!("Adding {} and {}", a, b);
    a + b
}

#[wasm_bindgen]
pub fn subtract(a: i32, b: i32) -> i32 {
    a - b
}

#[wasm_bindgen]
pub fn multiply(a: i32, b: i32) -> i32 {
    a * b
}

#[wasm_bindgen]
pub fn divide(a: i32, b: i32) -> i32 {
    if b == 0 {
        return 0;
    }
    a / b
}

#[wasm_bindgen]
pub fn fibonacci(n: i32) -> i32 {
    if n <= 0 {
        return 0;
    } else if n == 1 {
        return 1;
    }
    
    let mut a = 0;
    let mut b = 1;
    
    for _ in 2..=n {
        let temp = a + b;
        a = b;
        b = temp;
    }
    
    b
}

// String handling functions

#[wasm_bindgen]
pub fn allocate(size: usize) -> *mut u8 {
    // Create a new buffer with the specified size
    let mut buffer = Vec::with_capacity(size);
    // Ensure the buffer has the right size
    buffer.resize(size, 0);
    // Get a pointer to the buffer
    let ptr = buffer.as_mut_ptr();
    // Prevent the buffer from being deallocated when this function returns
    std::mem::forget(buffer);
    ptr
}

#[wasm_bindgen]
pub fn deallocate(ptr: *mut u8, size: usize) {
    // Recreate the Vec from the pointer and size
    unsafe {
        let _buffer = Vec::from_raw_parts(ptr, size, size);
        // Buffer will be deallocated when it goes out of scope
    }
}

#[wasm_bindgen]
pub fn process_string(ptr: *mut u8, len: usize) -> *mut u8 {
    // Read the input string
    let input = unsafe {
        let slice = std::slice::from_raw_parts(ptr, len);
        std::str::from_utf8(slice).unwrap_or("Invalid UTF-8")
    };
    
    // Process the string (in this case, reverse it)
    let result = format!("Processed: {}", input.chars().rev().collect::<String>());
    
    // Allocate memory for the result
    let result_bytes = result.as_bytes();
    let result_len = result_bytes.len();
    let result_ptr = allocate(result_len + 1); // +1 for null terminator
    
    // Copy the result to the allocated memory
    unsafe {
        std::ptr::copy_nonoverlapping(result_bytes.as_ptr(), result_ptr, result_len);
        // Add null terminator
        *result_ptr.add(result_len) = 0;
    }
    
    result_ptr
}

// Tests
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    fn test_subtract() {
        assert_eq!(subtract(5, 2), 3);
    }

    #[test]
    fn test_multiply() {
        assert_eq!(multiply(3, 4), 12);
    }

    #[test]
    fn test_divide() {
        assert_eq!(divide(10, 2), 5);
        assert_eq!(divide(5, 0), 0); // Test division by zero
    }

    #[test]
    fn test_fibonacci() {
        assert_eq!(fibonacci(0), 0);
        assert_eq!(fibonacci(1), 1);
        assert_eq!(fibonacci(2), 1);
        assert_eq!(fibonacci(3), 2);
        assert_eq!(fibonacci(4), 3);
        assert_eq!(fibonacci(5), 5);
        assert_eq!(fibonacci(6), 8);
        assert_eq!(fibonacci(10), 55);
    }
}