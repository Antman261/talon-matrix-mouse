matrix [show]: user.matrix_mouse_grid_start()
matrix clear: user.matrix_mouse_grid_stop()
matrix (<user.letters> | <user.number_key>):
  input = letters or number_key
  user.matrix_mouse(input)
matrix right (<user.letter> | <user.number_key>):
  input = letter or number_key
  user.matrix_mouse(input, "right")
