### 使用方式：

保持源代码仓库和测试仓库在同一级

在该仓库下hw05 目录下 创建yours和correct文件夹

```makefile
$ mkdir yours correct
```

在源代码仓库2024/hw5/Makefile中添加

```makefile
EXTERNAL_TEST_DIR = $(abspath $(CURDIR)/../../FDMJ-tests/hw05)
.PHONY: test-external clean-external gen-random clean-random

clean-external: clean-random
	@find $(EXTERNAL_TEST_DIR)/test -type f \( \
		-name "*.ll" -o -name "*.xml" -o -name "*.output" \
		-o -name "*.src" -o -name "*.ast" -o -name "*.irp" \
		\) -exec $(RM) {} \;
	@$(RM) $(EXTERNAL_TEST_DIR)/yours/*.debug
	@$(RM) $(EXTERNAL_TEST_DIR)/correct/*.debug

gen-random:
	@cd $(EXTERNAL_TEST_DIR); \
	python3 randomCodeGen.py; \
	cd $(CURDIR)

clean-random:
	@find $(EXTERNAL_TEST_DIR)/test -type f \( \
		-name "random*.fmj" \
		\) -exec $(RM) {} \;

test-external: clean-external gen-random
	@cd $(EXTERNAL_TEST_DIR)/test; \
	for file in $$(ls .); do \
		if [ "$${file##*.}" = "fmj" ]; then \
			echo "[$${file%%.*}]"; \
			$(FMJ2AST) "$${file%%.*}" && \
			$(MAIN_EXE) "$${file%%.*}" 2> ../yours/"$${file%%.*}".debug; \
		fi \
	done; \
	for file in $$(ls .); do \
		if [ "$${file##*.}" = "fmj" ]; then \
			echo "[$${file%%.*}]"; \
			$(FMJ2AST) "$${file%%.*}" && \
			$(ASTCHECK) "$${file%%.*}" 2> ../correct/"$${file%%.*}".debug; \
		fi \
	done; \
	cd $(EXTERNAL_TEST_DIR); \
	python3 check.py; \
	cd $(CURDIR)

```

并在该目录下运行

```shell
$ make test-external
```



### 贡献测试用例方式：

在该仓库./hw05/test中加入.fmj文件即可