import pytest
from app.core.sec_util import Util


class TestUtil:

    @pytest.mark.parametrize("input", [
        "abc",
        "abc123",
        "!@#$%",
        "alskdh123*(&*^(",
    ])

    def test_string_normal(self, input):
        assert Util(input).is_string() is input, "Test failed, input is not a string"    
        
    @pytest.mark.parametrize("input", [
        [1,2,3,4],
        1,
        (123, 123),
        {"asd":1},
        {"asd":"1"},
        ["123", "123"]
    ])

    def test_string_abnormal(self, input):
        assert Util(input).is_string() is False, "Test failed, input is a string"

    @pytest.mark.parametrize("input", [
        "abcjk",
        "abc"
    ])

    def test_is_string_alpha_normal(self, input):
        assert Util(input).is_alnum() is input, "Test failed, input is not alphabetic"    
        
    @pytest.mark.parametrize("input", [
        "!@#$%",
        "alskdh123*(&*^(",
        "a*(&*^(",
        "1*(&*^(",
    ])

    def test_is_string_alpha_abnormal(self, input):
        assert Util(input).is_alnum() is False, "Test failed, input is alphabetic"

    @pytest.mark.parametrize("input", [
        "1",
        "11",
        "123",
    ])

    def test_is_string_only_num_normal(self, input):
        assert Util(input).is_string_only_num() is input, "Test failed, input is not numeric"    
        
    @pytest.mark.parametrize("input", [
        "!@#$%",
        "alskdh123*(&*^(",
        "a*(&*^(",
        "1*(&*^(",
    ])

    def test_is_string_only_num_abnormal(self, input):
        assert Util(input).is_string_only_num() is False, "Test failed, input is a numeric"

    @pytest.mark.parametrize("input", [
        "1a",
        "11a",
        "123",
        "asd"
    ])

    def test_is_alnum_normal(self, input):
        assert Util(input).is_alnum() is input, "Test failed, input is not alpha numeric"    
        
    @pytest.mark.parametrize("input", [
        "!@#$%",
        "alskdh123*(&*^(",
        "a*(&*^(",
        "1*(&*^(",
    ])

    def test_is_alnum_abnormal(self, input):
        assert Util(input).is_alnum() is False, "Test failed, input is a alpha numeric"

    @pytest.mark.parametrize("input", [

        {"asd":"1"},
        {"asd":1},
        {"asd!":1}
    ])

    def test_is_dict_normal(self, input):
        assert Util(input).is_dict() is input, "Test failed, input is not a dict"    
        
    @pytest.mark.parametrize("input", [
        "!@#$%",
        "[alskdh123*(&*^(]",
        "(a*(&*^()",
        1,
    ])

    def test_is_dict_abnormal(self, input):
        assert Util(input).is_dict() is False, "Test failed, input is a dict"

    @pytest.mark.parametrize("input", [

        {"asd":"my.owns*ite@our-earth.oa"},
        {"1":"my.owns*ite@our-earth.oa"},
        {"1asd":"my.owns*ite@our-earth.oa"}
    ])

    def test_is_dict_and_email_normal(self, input):
        assert Util(input).is_dict_and_alphanumeric() is input, "Test failed, input is a dict and alphanumeric"    
        
    @pytest.mark.parametrize("input", [
        {"asd":"my.oqw*iteour-ewqeh.oa"},
        {"1":"my.oasde@our-earthoa"},
        {"1asd":"masdh.oa"},
        {"asd!":"1"}
    ])

    def test_is_dict_and_email_abnormal(self, input):
        assert Util(input).is_dict_and_alphanumeric() is False, "Test failed, input is not a dict and alphanumeric"

    @pytest.mark.parametrize("input", [

        "my.owns*ite@our-earth.sg",
        "asdns*ite@ogmailth.oa",
        "my.owns*ite@our-earth.com"
    ])

    def test_is_email_normal(self, input):
        assert Util(input).is_email() is input, "Test failed, input is a dict and alphanumeric"    
        
    @pytest.mark.parametrize("input", [
        "myasd.oqw*iteour-ewqeh.oa",
        "my.oasde@oasdur-earthoa",
        "masdh.oa",
        "1"
    ])

    def test_is_email_abnormal(self, input):
        assert Util(input).is_email() is False, "Test failed, input is not a dict and alphanumeric"
    
    @pytest.mark.parametrize("input, min, max", [
        ["asdfsd",1,10],
        ["a",1,10],
        ["adasda",1,10]
    ])

    def test_check_bound_normal(self, input, min, max):
        assert Util(input, min, max).check_bound() is True, "Test failed, input is outside bound"    
        
    @pytest.mark.parametrize("input, min, max", [
        ["",1,10],
        ["aaaaaaaaaaasdasjgkjfur76daa",1,10],
    ])

    def test_check_bound_abnormal(self, input, min, max):
        assert Util(input, min, max).check_bound() is False, "Test failed, input is inside bound"

    @pytest.mark.parametrize("input", [
        "\"asd\",1,10",
        "asasd",
        "asdasd123",
        "as!$%^",
        "asd asd",
    ])

    def test_check_content_normal(self, input):
        assert Util(input).check_content() is input, "Test failed, input is outside bound"    
        
    @pytest.mark.parametrize("input", [
        "<>"
        "<script>",
        "<a href>",
        "https://sdfs.sdfsdf.com/sdfsdf/sdfsdf/sd/sdfsdfs?bob=%20tree&jef=man sdds",
        "https://www. usatoday.com/story/news/wor ld/2018/01/02/mountains-u-s-recycling-pile-up-china-restricts-imports/995134001/",
        "I liked a @YouTube video http://youtu.be/7P9 hello"
    ])

    def test_check_content_abnormal(self, input):
        assert Util(input).check_content() is False, "Test failed, input is not a dict and alphanumeric"
