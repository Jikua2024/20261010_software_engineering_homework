# -*- coding: utf-8 -*-
"""
timetable.py 核心逻辑单元测试

仅测试不依赖 GUI 的部分：
    - parse_weeks
    - Course 数据类
    - sample_courses
    - course_color
"""

import unittest
import re

import timetable
from timetable import parse_weeks, Course, sample_courses, course_color


# ===========================================================================
# parse_weeks 测试
# ===========================================================================
class TestParseWeeks(unittest.TestCase):
    """测试周次字符串解析函数 parse_weeks。"""

    # ---------- 基础范围格式 ----------
    def test_range_1_12(self):
        """解析 "1-12周" 应返回 {1..12}。"""
        self.assertEqual(parse_weeks("1-12周"), set(range(1, 13)))

    def test_range_2_16(self):
        """解析 "2-16周" 应返回 {2..16}。"""
        self.assertEqual(parse_weeks("2-16周"), set(range(2, 17)))

    def test_range_5_15(self):
        """解析 "5-15周" 应返回 {5..15}。"""
        self.assertEqual(parse_weeks("5-15周"), set(range(5, 16)))

    def test_range_1_8(self):
        """解析 "1-8周" 应返回 {1..8}。"""
        self.assertEqual(parse_weeks("1-8周"), set(range(1, 9)))

    def test_range_1_11(self):
        """解析 "1-11周" 应返回 {1..11}。"""
        self.assertEqual(parse_weeks("1-11周"), set(range(1, 12)))

    def test_range_1_16(self):
        """解析 "1-16周" 应返回 {1..16}。"""
        self.assertEqual(parse_weeks("1-16周"), set(range(1, 17)))

    # ---------- 单周格式 ----------
    def test_single_week_with_第(self):
        """解析 "第1周" 应返回 {1}。"""
        self.assertEqual(parse_weeks("第1周"), {1})

    def test_single_week_plain(self):
        """解析 "1周" 应返回 {1}。"""
        self.assertEqual(parse_weeks("1周"), {1})

    # ---------- 多段格式 ----------
    def test_multi_range_with_comma(self):
        """解析 "1-8,10-12周" 应返回 {1..8, 10..12}。"""
        expected = set(range(1, 9)) | set(range(10, 13))
        self.assertEqual(parse_weeks("1-8,10-12周"), expected)

    def test_multi_single_with_comma(self):
        """解析 "1,3,5周" 应返回 {1, 3, 5}。"""
        self.assertEqual(parse_weeks("1,3,5周"), {1, 3, 5})

    def test_mixed_range_and_single(self):
        """解析 "1-4,6,8-10周" 应返回 {1,2,3,4,6,8,9,10}。"""
        expected = {1, 2, 3, 4, 6, 8, 9, 10}
        self.assertEqual(parse_weeks("1-4,6,8-10周"), expected)

    # ---------- 边界与空值 ----------
    def test_empty_string(self):
        """空字符串应返回空集合。"""
        self.assertEqual(parse_weeks(""), set())

    def test_none_returns_empty(self):
        """None（falsy）输入应返回空集合。"""
        self.assertEqual(parse_weeks(None), set())

    def test_whitespace_string(self):
        """仅含空白字符的字符串应返回空集合。"""
        self.assertEqual(parse_weeks("   "), set())

    def test_leading_trailing_whitespace(self):
        """首尾空白应被忽略。"""
        self.assertEqual(parse_weeks("  1-4周  "), {1, 2, 3, 4})

    def test_whitespace_around_comma(self):
        """逗号周围的空白应被忽略。"""
        self.assertEqual(parse_weeks("1-3, 5-6周"), {1, 2, 3, 5, 6})

    def test_single_week_no_suffix(self):
        """不带"周"后缀的单周数字。"""
        self.assertEqual(parse_weeks("3"), {3})

    def test_range_no_suffix(self):
        """不带"周"后缀的范围。"""
        self.assertEqual(parse_weeks("2-5"), {2, 3, 4, 5})

    def test_single_week_第_no_suffix(self):
        """带"第"字但不带"周"后缀，如 "第7"。"""
        self.assertEqual(parse_weeks("第7"), {7})

    def test_empty_part_after_comma(self):
        """逗号后为空段应被忽略而非抛异常。"""
        self.assertEqual(parse_weeks("1-2,"), {1, 2})

    def test_第字在中间位置(self):
        """'第' 字的全局替换可能导致异常，测试 "第1-第3周"。"""
        # 当前实现把所有"第"替换为空，结果为 "1-3"
        result = parse_weeks("第1-第3周")
        self.assertEqual(result, {1, 2, 3})

    # ---------- 非法输入 ----------
    def test_invalid_non_numeric_returns_empty(self):
        """包含非数字字符应返回空集合。"""
        self.assertEqual(parse_weeks("abc周"), set())

    def test_invalid_range_letters_returns_empty(self):
        """范围中含字母应返回空集合。"""
        self.assertEqual(parse_weeks("a-b周"), set())

    def test_invalid_trailing_text_returns_empty(self):
        """数字后跟其它文字（不只是"周"）应返回空集合。"""
        self.assertEqual(parse_weeks("1-4周半"), set())


# ===========================================================================
# Course 数据类测试
# ===========================================================================
class TestCourse(unittest.TestCase):
    """测试 Course 数据类字段。"""

    def test_course_fields(self):
        """Course 应包含所有规定字段且可正确赋值。"""
        c = Course(name="测试课", day=2, start=1, end=2,
                   weeks="1-16周", campus="闵行", location="上院101")
        self.assertEqual(c.name, "测试课")
        self.assertEqual(c.day, 2)
        self.assertEqual(c.start, 1)
        self.assertEqual(c.end, 2)
        self.assertEqual(c.weeks, "1-16周")
        self.assertEqual(c.campus, "闵行")
        self.assertEqual(c.location, "上院101")

    def test_course_is_dataclass(self):
        """Course 应是 dataclass。"""
        import dataclasses
        self.assertTrue(dataclasses.is_dataclass(Course))

    def test_course_field_count(self):
        """Course 应有 7 个字段。"""
        import dataclasses
        self.assertEqual(len(dataclasses.fields(Course)), 7)

    def test_course_field_names(self):
        """Course 字段名应为 name/day/start/end/weeks/campus/location。"""
        import dataclasses
        names = [f.name for f in dataclasses.fields(Course)]
        self.assertEqual(names,
                         ["name", "day", "start", "end", "weeks", "campus", "location"])


# ===========================================================================
# sample_courses 测试
# ===========================================================================
class TestSampleCourses(unittest.TestCase):
    """测试预加载课表数据。"""

    def setUp(self):
        self.courses = sample_courses()

    def test_count_is_20(self):
        """sample_courses 应返回 20 门课。"""
        self.assertEqual(len(self.courses), 20)

    def test_all_are_course_instances(self):
        """所有元素都应是 Course 实例。"""
        for c in self.courses:
            self.assertIsInstance(c, Course)

    def test_all_day_in_range(self):
        """所有 day 应在 0-4 之间。"""
        for c in self.courses:
            self.assertIn(c.day, range(5),
                          "课程 {} 的 day={} 不在 0-4".format(c.name, c.day))

    def test_all_start_end_valid(self):
        """所有 start/end 应满足 1 <= start <= end <= 13。"""
        for c in self.courses:
            self.assertTrue(1 <= c.start <= c.end <= 13,
                            "课程 {} 节次 {}-{} 不合法".format(c.name, c.start, c.end))

    def test_all_weeks_parseable(self):
        """所有 weeks 字符串都应能被 parse_weeks 解析为非空集合。"""
        for c in self.courses:
            weeks = parse_weeks(c.weeks)
            self.assertGreater(len(weeks), 0,
                               "课程 {} 的周次 {} 解析为空".format(c.name, c.weeks))

    # ---------- 关键数据点验证 ----------
    def test_monday_period_3_4_has_two_courses(self):
        """周一(day=0) 3-4 节应有两门课：生产计划与控制、计算复杂性。"""
        target = [c for c in self.courses
                  if c.day == 0 and c.start == 3 and c.end == 4]
        names = {c.name for c in target}
        self.assertEqual(len(target), 2)
        self.assertEqual(names, {"生产计划与控制", "计算复杂性"})

    def test_thursday_period_1_2_is_complexity(self):
        """周四(day=3) 1-2 节应为计算复杂性。"""
        target = [c for c in self.courses
                  if c.day == 3 and c.start == 1 and c.end == 2]
        self.assertEqual(len(target), 1)
        self.assertEqual(target[0].name, "计算复杂性")

    def test_monday_period_3_4_schedule_and_control_location(self):
        """周一 3-4 节的生产计划与控制地点应为下院312。"""
        target = [c for c in self.courses
                  if c.day == 0 and c.start == 3 and c.end == 4
                  and c.name == "生产计划与控制"]
        self.assertEqual(len(target), 1)
        self.assertEqual(target[0].location, "下院312")
        self.assertEqual(target[0].weeks, "1-12周")

    def test_monday_period_3_4_complexity_location(self):
        """周一 3-4 节的计算复杂性地点应为东下院311。"""
        target = [c for c in self.courses
                  if c.day == 0 and c.start == 3 and c.end == 4
                  and c.name == "计算复杂性"]
        self.assertEqual(len(target), 1)
        self.assertEqual(target[0].location, "东下院311")
        self.assertEqual(target[0].weeks, "1-12周")

    def test_wednesday_insurance_course(self):
        """周三(day=2) 11-13 节应为 中国医疗保险制度的转型发展与创新，5-15周。"""
        target = [c for c in self.courses
                  if c.day == 2 and c.start == 11 and c.end == 13]
        self.assertEqual(len(target), 1)
        self.assertEqual(target[0].name, "中国医疗保险制度的转型发展与创新")
        self.assertEqual(target[0].weeks, "5-15周")

    def test_friday_engineering_and_society(self):
        """周五(day=4) 7-9 节应为 工程与社会，1-11周。"""
        target = [c for c in self.courses
                  if c.day == 4 and c.start == 7 and c.end == 9]
        self.assertEqual(len(target), 1)
        self.assertEqual(target[0].name, "工程与社会")
        self.assertEqual(target[0].weeks, "1-11周")

    def test_monday_modeling_simulation_two_entries(self):
        """生产系统建模与仿真 周一 6-8 节应有两条（第1周 和 2-16周）。"""
        target = [c for c in self.courses
                  if c.name == "生产系统建模与仿真" and c.day == 0
                  and c.start == 6 and c.end == 8]
        self.assertEqual(len(target), 2)
        week_sets = {c.weeks for c in target}
        self.assertEqual(week_sets, {"第1周", "2-16周"})

    def test_thursday_optimization_12_13(self):
        """周四 12-13 节应为 优化算法设计，1-8周。"""
        target = [c for c in self.courses
                  if c.day == 3 and c.start == 12 and c.end == 13]
        self.assertEqual(len(target), 1)
        self.assertEqual(target[0].name, "优化算法设计")
        self.assertEqual(target[0].weeks, "1-8周")

    def test_distribution_by_day(self):
        """按天分布：周一6、周二4、周三2、周四5、周五3。"""
        from collections import Counter
        cnt = Counter(c.day for c in self.courses)
        self.assertEqual(cnt[0], 6)
        self.assertEqual(cnt[1], 4)
        self.assertEqual(cnt[2], 2)
        self.assertEqual(cnt[3], 5)
        self.assertEqual(cnt[4], 3)


# ===========================================================================
# course_color 测试
# ===========================================================================
class TestCourseColor(unittest.TestCase):
    """测试课程配色函数。"""

    HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

    def _hex_to_rgb(self, h):
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    def test_format_is_hex(self):
        """返回值应为 6 位 hex（#RRGGBB）。"""
        for i in range(20):
            color = course_color(i)
            self.assertRegex(color, self.HEX_RE,
                             "索引 {} 返回 {} 不是合法 6 位 hex".format(i, color))

    def test_blue_family(self):
        """B 分量应 >= R 且 >= G（蓝色系）。"""
        for i in range(20):
            r, g, b = self._hex_to_rgb(course_color(i))
            self.assertGreaterEqual(b, r,
                                    "索引 {} 颜色 B={} < R={}".format(i, b, r))
            self.assertGreaterEqual(b, g,
                                    "索引 {} 颜色 B={} < G={}".format(i, b, g))

    def test_distinct_colors_for_distinct_indices(self):
        """前 8 个索引的颜色应互不相同（明度循环步长使它们可区分）。"""
        colors = {course_color(i) for i in range(8)}
        self.assertEqual(len(colors), 8)

    def test_color_length(self):
        """颜色字符串长度应为 7（# + 6 位）。"""
        for i in range(20):
            self.assertEqual(len(course_color(i)), 7)

    def test_color_starts_with_hash(self):
        """颜色字符串应以 # 开头。"""
        for i in range(20):
            self.assertTrue(course_color(i).startswith("#"))

    def test_negative_index_no_crash(self):
        """负索引不应崩溃（取模后仍可计算）。"""
        # 不抛异常即可
        color = course_color(-1)
        self.assertRegex(color, self.HEX_RE)


# ===========================================================================
if __name__ == "__main__":
    unittest.main(verbosity=2)
