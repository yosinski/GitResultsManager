all : demo-c run-demos

demo-c : demo-c.cc
	g++ -o $@ $<

run-demos :
	@echo
	@echo "Running demo: demo-c"
	resman ./demo-c
	@echo
	@echo "Running demo: snoozer.py "
	resman ./snoozer.py
	@echo
	@echo "Running demo: demo-python.py "
	resman ./demo-python.py
	@echo
	@echo "Running demo: demo-python-with-flush.py "
	resman ./demo-python-with-flush.py
	@echo
	@echo "Running demo: demo-GRM-module.py"
	./demo-GRM-module.py

clean :
	rm -f demo-c
