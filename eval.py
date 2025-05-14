from bs4 import BeautifulSoup
import re
import colorsys

def html_structure_reward_func(completions, **kwargs) -> list[float]:
    from bs4 import BeautifulSoup
    import re
    import colorsys

    def extract_colors(text):
        hex_colors = re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}', text)
        rgb_colors = re.findall(r'rgb[a]?\([^)]*\)', text)
        return hex_colors + rgb_colors

    def color_to_hsl(color):
        try:
            if color.startswith('#'):
                hex_color = color.lstrip('#')
                if len(hex_color) == 3:
                    hex_color = ''.join([c*2 for c in hex_color])
                r, g, b = [int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4)]
            elif color.startswith('rgb'):
                nums = [int(float(n.strip('% '))) for n in re.findall(r'\d+\.?\d*', color)[:3]]
                r, g, b = [n / 255.0 for n in nums]
            else:
                return None
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            return (h, s, l)
        except:
            return None

    def color_harmony_score(colors):
        hsl_colors = [color_to_hsl(c) for c in colors]
        hsl_colors = [c for c in hsl_colors if c]
        if len(hsl_colors) < 2:
            return 1.0
        hue_vals = [c[0] for c in hsl_colors]
        hue_diffs = [abs(h1 - h2) for i, h1 in enumerate(hue_vals) for h2 in hue_vals[i+1:]]
        avg_diff = sum(hue_diffs) / len(hue_diffs)
        if avg_diff < 0.05 or avg_diff > 0.5:
            return 0.3
        elif 0.1 <= avg_diff <= 0.3:
            return 1.0
        else:
            return 0.7

    responses = [completion[0]["content"] for completion in completions]
    scores = []

    for html_content in responses:
        try:
            if "<html" not in html_content or "<body" not in html_content:
                scores.append(0.0)
                continue

            soup = BeautifulSoup(html_content, 'html.parser')
            score = 100.0

            # 1. 구조 평가
            if not html_content.lower().startswith('<!doctype'):
                score -= 20.0
            html_tag = soup.find('html')
            if not html_tag or not html_tag.get('lang'):
                score -= 10.0
            if not soup.find('meta', attrs={'name': 'viewport'}):
                score -= 10.0
            headings = soup.find_all(['h1', 'h2', 'h3'])
            if not headings:
                score -= 8.0
            elif not soup.find('h1'):
                score -= 5.0
            semantic_tags = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
            used_tags = set()

            for tag in semantic_tags:
                if soup.find(tag):
                    used_tags.add(tag)

            semantic_count = len(used_tags)

            # 기준: 7개 중 사용한 개수 비율
            # 4개 이상 → 보너스, 2~3개 → 무감점, 0~1개 → 감점
            if semantic_count >= 4:
                score += 2.0  # 풍부하게 사용
            elif semantic_count <= 1:
                score -= 5.0  # 거의 없음
            elif semantic_count == 2:
                score -= 2.0  # 부족
            div_count = len(soup.find_all('div'))
            total_elements = len(soup.find_all())
            if total_elements > 0 and (div_count / total_elements) > 0.7:
                score -= 5.0
            for form in soup.find_all('form'):
                for input_tag in form.find_all('input'):
                    if not input_tag.get('id'):
                        score -= 1.0

            # 2. 반응형 단위 평가
            fixed_unit_penalty = 0
            style_text = html_content.lower()
            fixed_units = re.findall(r'(?:style\s*=\s*["\'][^"\']*?)(\d+(px|pt|cm|mm))', style_text)
            if fixed_units:
                fixed_unit_penalty += len(fixed_units) * 1.5
            for style in soup.find_all('style'):
                if 'px' in style.text:
                    fixed_unit_penalty += style.text.count('px') * 1.0
            score -= min(fixed_unit_penalty, 10.0)

            responsive_bonus = 0
            for unit in ['%', 'vw', 'vh', 'em', 'rem']:
                if unit in style_text:
                    responsive_bonus += 0.5
            score += min(responsive_bonus, 2.5)

            # 3. 색상 조화도 평가
            color_values = extract_colors(html_content)
            harmony = color_harmony_score(color_values)
            if harmony < 0.4:
                score -= 5.0
            elif harmony > 0.8:
                score += 3.0
            elif harmony > 0.6:
                score += 1.5

            # 4. CSS 존재 여부 평가
            style_tags = soup.find_all('style')
            inline_styles = re.findall(r'style\s*=\s*["\']', html_content)
            class_attrs = re.findall(r'class\s*=\s*["\']', html_content)

            css_score_penalty = 0
            if not style_tags:
                css_score_penalty += 5.0
            if not inline_styles:
                css_score_penalty += 5.0
            if not class_attrs:
                css_score_penalty += 3.0
            score -= css_score_penalty

            # 최종 점수 정규화
            normalized = max(0.0, min(score, 100.0)) / 100.0
            scores.append(normalized)

        except Exception:
            scores.append(0.0)

    return scores

class RewardFunc:
    def __init__(self, completions, **kwargs):
        self.completions = completions
        self.kwargs = kwargs
        self.responses = [completion[0]["content"] for completion in completions]
    
    def extract_colors(self, text):
        hex_colors = re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}', text)
        rgb_colors = re.findall(r'rgb[a]?\([^)]*\)', text)
        return hex_colors + rgb_colors
    def color_to_hsl(self, color):
        try:
            if color.startswith('#'):
                hex_color = color.lstrip('#')
                if len(hex_color) == 3:
                    hex_color = ''.join([c*2 for c in hex_color])
                r, g, b = [int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4)]
            elif color.startswith('rgb'):
                nums = [int(float(n.strip('% '))) for n in re.findall(r'\d+\.?\d*', color)[:3]]
                r, g, b = [n / 255.0 for n in nums]
            else:
                return None
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            return (h, s, l)
        except:
            return None
    def color_harmony_score(self, colors):
        hsl_colors = [self.color_to_hsl(c) for c in colors]
        hsl_colors = [c for c in hsl_colors if c]
        if len(hsl_colors) < 2:
            return 1.0
        hue_vals = [c[0] for c in hsl_colors]
        hue_diffs = [abs(h1 - h2) for i, h1 in enumerate(hue_vals) for h2 in hue_vals[i+1:]]
        avg_diff = sum(hue_diffs) / len(hue_diffs)
        if avg_diff < 0.05 or avg_diff > 0.5:
            return 0.3
        elif 0.1 <= avg_diff <= 0.3:
            return 1.0
        else:
            return 0.7
    
    def structure_eval(self, html_content):
        score = 0
        soup = BeautifulSoup(html_content, 'html.parser')
        if not html_content.lower().startswith('<!doctype'):
            score -= 20.0
        html_tag = soup.find('html')
        if not html_tag or not html_tag.get('lang'):
            score -= 10.0
        if not soup.find('meta', attrs={'name': 'viewport'}):
            score -= 10.0
        headings = soup.find_all(['h1', 'h2', 'h3'])
        if not headings:
            score -= 8.0
        elif not soup.find('h1'):
            score -= 5.0
        semantic_tags = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
        used_tags = set()
        for tag in semantic_tags:
            if soup.find(tag):
                used_tags.add(tag)
        semantic_count = len(used_tags)
        if semantic_count >= 4:
            score += 2.0
        elif semantic_count <= 1:
            score -= 5.0
        elif semantic_count == 2:
            score -= 2.0
        div_count = len(soup.find_all('div'))
        total_elements = len(soup.find_all())
        if total_elements > 0 and (div_count / total_elements) > 0.7:
            score -= 5.0
        for form in soup.find_all('form'):
            for input_tag in form.find_all('input'):
                if not input_tag.get('id'):
                    score -= 1.0
        return score

    def eval(self):
        scores = []
        for html_content in self.responses:
            if "<html" not in html_content or "<body" not in html_content:
                scores.append(0.0)
                continue
            score = 100.0
            # 1. 구조 평가
            score += min(0, self.structure_eval(html_content))
            # 2. 반응형 단위 평가



    

def html_structure_reward_func_v3(completions, **kwargs) -> list[float]:
    from bs4 import BeautifulSoup
    import re
    import colorsys

    def parse_color(color):
        try:
            color = color.strip()
            if color.startswith('#'):
                hex_color = color[1:]
                if len(hex_color) == 3:
                    hex_color = ''.join([c * 2 for c in hex_color])
                r, g, b = [int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
            elif 'rgb' in color:
                nums = [int(n) for n in re.findall(r'\d+', color)]
                r, g, b = [n / 255 for n in nums[:3]]
            else:
                return None
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            return h
        except:
            return None

    def estimate_area(style):
        width = height = 0
        if style:
            width_match = re.search(r'width\s*:\s*(\d+)(px|%)', style)
            height_match = re.search(r'height\s*:\s*(\d+)(px|%)', style)
            try:
                if width_match and width_match.group(2) == 'px':
                    width = int(width_match.group(1))
                if height_match and height_match.group(2) == 'px':
                    height = int(height_match.group(1))
                print("debug", width, height)
            except:
                pass
        return max(width * height, 1)

    def weighted_color_harmony_score(soup):
        elements = soup.find_all(style=True)
        hue_weights = []

        for el in elements:
            style = el.get('style', '')
            area = estimate_area(style)

            for attr in ['background-color', 'color', 'border-color']:
                match = re.search(f'{attr}\s*:\s*([^;]+)', style)
                if match:
                    color = match.group(1)
                    hue = parse_color(color)
                    if hue is not None:
                        hue_weights.append((hue, area))
                        break

        if len(hue_weights) < 2:
            return 1.0

        weighted_diffs = []
        for i in range(len(hue_weights)):
            for j in range(i + 1, len(hue_weights)):
                h1, w1 = hue_weights[i]
                h2, w2 = hue_weights[j]
                diff = abs(h1 - h2)
                weight = (w1 + w2) / 2
                weighted_diffs.append(diff * weight)

        total_weight = sum((w1 + w2) / 2 for i, (h1, w1) in enumerate(hue_weights)
                                              for j, (h2, w2) in enumerate(hue_weights) if j > i)
        avg_weighted_diff = sum(weighted_diffs) / total_weight if total_weight else 0

        if avg_weighted_diff < 0.05 or avg_weighted_diff > 0.5:
            return 0.3
        elif 0.1 <= avg_weighted_diff <= 0.3:
            return 1.0
        else:
            return 0.7

    responses = [completion[0]["content"] for completion in completions]
    scores = []

    for html_content in responses:
        try:
            if "<html" not in html_content or "<body" not in html_content:
                scores.append(0.0)
                continue

            soup = BeautifulSoup(html_content, 'html.parser')
            score = 100.0

            if not html_content.lower().startswith('<!doctype'):
                score -= 20.0
            html_tag = soup.find('html')
            if not html_tag or not html_tag.get('lang'):
                score -= 10.0
            if not soup.find('meta', attrs={'name': 'viewport'}):
                score -= 10.0
            headings = soup.find_all(['h1', 'h2', 'h3'])
            if not headings:
                score -= 8.0
            elif not soup.find('h1'):
                score -= 5.0
            semantic_tags = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
            used_tags = set()
            for tag in semantic_tags:
                if soup.find(tag):
                    used_tags.add(tag)
            semantic_count = len(used_tags)
            if semantic_count >= 4:
                score += 2.0
            elif semantic_count <= 1:
                score -= 5.0
            elif semantic_count == 2:
                score -= 2.0
            div_count = len(soup.find_all('div'))
            total_elements = len(soup.find_all())
            if total_elements > 0 and (div_count / total_elements) > 0.7:
                score -= 5.0
            for form in soup.find_all('form'):
                for input_tag in form.find_all('input'):
                    if not input_tag.get('id'):
                        score -= 1.0

            fixed_unit_penalty = 0
            style_text = html_content.lower()
            fixed_units = re.findall(r'(?:style\s*=\s*[\"\'][^\"\']*?)(\d+(px|pt|cm|mm))', style_text)
            if fixed_units:
                fixed_unit_penalty += len(fixed_units) * 1.5
            for style in soup.find_all('style'):
                if 'px' in style.text:
                    fixed_unit_penalty += style.text.count('px') * 1.0
            score -= min(fixed_unit_penalty, 10.0)

            responsive_bonus = 0
            for unit in ['%', 'vw', 'vh', 'em', 'rem']:
                if unit in style_text:
                    responsive_bonus += 0.5
            score += min(responsive_bonus, 2.5)

            # updated: weighted color harmony
            harmony = weighted_color_harmony_score(soup)
            if harmony < 0.4:
                score -= 5.0
            elif harmony > 0.8:
                score += 3.0
            elif harmony > 0.6:
                score += 1.5

            style_tags = soup.find_all('style')
            inline_styles = re.findall(r'style\s*=\s*[\"\']', html_content)
            class_attrs = re.findall(r'class\s*=\s*[\"\']', html_content)
            css_score_penalty = 0
            if not style_tags:
                css_score_penalty += 5.0
            if not inline_styles:
                css_score_penalty += 5.0
            if not class_attrs:
                css_score_penalty += 3.0
            score -= css_score_penalty

            normalized = max(0.0, min(score, 100.0)) / 100.0
            scores.append(normalized)

        except Exception:
            scores.append(0.0)

    return scores
