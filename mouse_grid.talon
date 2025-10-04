matrix [show]: user.matrix_mouse_grid_start()
matrix clear: user.matrix_mouse_grid_stop()
matrix (gaze | look): user.matrix_gaze_range(3)
matrix [(gaze | look)] zone: user.matrix_gaze("zone")
matrix [(gaze | look)] cell: user.matrix_gaze("cell")
matrix (gaze | look) subcell: user.matrix_gaze("subcell")
matrix (<user.letters> | <user.number_key>):
  input = letters or number_key
  user.matrix_mouse(input)
matrix right (<user.letter> | <user.number_key>):
  input = letter or number_key
  user.matrix_mouse(input, "right")
