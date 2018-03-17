# extract_kern_size
Simple script to extract linux kernel struct sizes.

# Current Usage
Since this script is extremely simple, I may not put it on Pypi.

Dependencies:
* python3
* elftools(for extracting DWARF info from image)

You also need a kernel image compiled with struct info, since default kernel debug info is at 
default level, you need to do something manually.

As for me, I searched `-g` across global kernel `Makefile` at the root of linux source tree
and edited it to `-g3` to generate struct info as well.

When you finished compile, you'll get a kernel image with struct type info in it. Now the script
is on.
Run it like this:
```
python extract_kernel_size.py vmlinux sizes.db
```
Note that `sizes.db` contains the output `sqlite3` database, and it must not exist.
