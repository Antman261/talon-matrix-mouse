matrix show: user.mouse_grid_start()
matrix clear: user.mouse_grid_stop()
matrix (<user.letters> | <user.number_key>):
  input = letters or number_key
  user.vox_mouse(input)
matrix right (<user.letter> | <user.number_key>):
  input = letter or number_key
  user.vox_mouse(input, "right")
