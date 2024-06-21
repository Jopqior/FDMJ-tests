将测试文件（.fmj文件）和期待输出（.ans文件）放在test目录下

```makefile
TEST_EXTERNAL_DIR=../FDMJ-tests
TEXT_EXTERNAL_HW=final
TESTFILE_EXTERNAL_DIR=$(TEST_EXTERNAL_DIR)/$(TEXT_EXTERNAL_HW)/test
CHECK_PY_SCRIPT := check.py

clean_external: 
	@$(RM) $(TEST_EXTERNAL_DIR)/$(TEXT_EXTERNAL_HW)/yours
	@$(RM) $(TEST_EXTERNAL_DIR)/$(TEXT_EXTERNAL_HW)/correct
	
	@find $(TESTFILE_EXTERNAL_DIR) -type f \( \
		-name "*.txt" -o -name "*.ast" -o -name "*.src" -o -name "*.xml" -o -name "*.irp"  \
		-o -name "*.stm" -o -name "*.ins" -o -name "*.cfg" -o -name "*.ssa" -o -name "*.ll" \
		-o -name "*.output" -o -name "gen_program_*" \
		-o -name "*.s" -o -name "*.arm" -o -name "*.rpi" -o -name "*.debug" -o -name "*.ig" \
	\) -exec $(RM) {} \; ;\

test_llvm: clean build clean_external
	@mkdir -p $(TEST_EXTERNAL_DIR)/$(TEXT_EXTERNAL_HW)/yours
	@mkdir -p $(TEST_EXTERNAL_DIR)/$(TEXT_EXTERNAL_HW)/correct
	@cd $(TESTFILE_EXTERNAL_DIR); \
	for file in $$(ls .); do \
		if [ "$${file##*.}" = "fmj" ]; then \
			echo "[$${file%%.*}]"; \
			$(MAIN_EXE) "$${file%%.*}" -c 0 < "$${file%%.*}".fmj; \
			$(MAIN_EXE) "$${file%%.*}" -c 1 < "$${file%%.*}".fmj; \
			$(LLVMLINK) --opaque-pointers "$${file%%.*}".7.ssa $(BUILD_DIR)/vendor/libsysy/libsysy64.ll -S -o "$${file%%.*}".ll && \
			$(LLI) -opaque-pointers "$${file%%.*}".ll > "$${file%%.*}".output; \
			mv "$${file%%.*}.output" "../yours/$${file%%.*}".txt; \
			cp "$${file%%.*}.ans" "../correct/$${file%%.*}".txt; \
		fi; \
	done; \
	python3 ../${CHECK_PY_SCRIPT}; \
	cd $(CURDIR)

test_rpi: clean build clean_external
	@mkdir -p $(TEST_EXTERNAL_DIR)/$(TEXT_EXTERNAL_HW)/yours
	@mkdir -p $(TEST_EXTERNAL_DIR)/$(TEXT_EXTERNAL_HW)/correct
	@cd $(TESTFILE_EXTERNAL_DIR); \
	for file in $$(ls .); do \
		if [ "$${file##*.}" = "fmj" ]; then \
			echo "[$${file%%.*}]"; \
			$(MAIN_EXE) "$${file%%.*}" -c 0 < "$${file%%.*}".fmj; \
			$(MAIN_EXE) "$${file%%.*}" -c 1 < "$${file%%.*}".fmj; \
			$(ARMCC) -mcpu=cortex-a72 "$${file%%.*}".10.s $(BUILD_DIR)/vendor/libsysy/libsysy32.s --static -o "$${file%%.*}".s; \
			$(QEMU) -B 0x1000 "$${file%%.*}".s > "$${file%%.*}".output; \
			mv "$${file%%.*}.output" "../yours/$${file%%.*}".txt; \
			cp "$${file%%.*}.ans" "../correct/$${file%%.*}".txt; \
		fi; \
	done; \
	python3 ../${CHECK_PY_SCRIPT}; \
	cd $(CURDIR)
```