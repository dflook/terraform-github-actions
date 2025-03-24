resource "local_file" "one" {
    filename = "test"
    content  = "this is my first file"
}

resource "local_file" "two" {
    filename = "test2"
    content  = "this is my second file"
}

resource "local_file" "three" {
    filename = "test3"
    content  = "this is my third file"
}
