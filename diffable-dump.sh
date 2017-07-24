sed -i -e 's/cookie[^,]*, //' $1
sed -i -e 's/duration[^,]*, //' $1
sed -i -e 's/n_packets[^,]*, //' $1
sed -i -e 's/n_bytes[^,]*, //' $1
sed -i -e 's/0x[0-9a-f]*//g' $1
