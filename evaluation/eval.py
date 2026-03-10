from bs4 import BeautifulSoup
import re
import colorsys

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
        self.soup = BeautifulSoup(html_content, 'html.parser')
        if not html_content.lower().startswith('<!doctype'):
            score -= 20.0
        html_tag = self.soup.find('html')
        if not html_tag or not html_tag.get('lang'):
            score -= 10.0
        if not self.soup.find('meta', attrs={'name': 'viewport'}):
            score -= 10.0
        headings = self.soup.find_all(['h1', 'h2', 'h3'])
        if not headings:
            score -= 8.0
        elif not self.soup.find('h1'):
            score -= 5.0
        semantic_tags = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
        used_tags = set()
        for tag in semantic_tags:
            if self.soup.find(tag):
                used_tags.add(tag)
        semantic_count = len(used_tags)
        if semantic_count >= 4:
            score += 2.0
        elif semantic_count <= 1:
            score -= 5.0
        elif semantic_count == 2:
            score -= 2.0
        div_count = len(self.soup.find_all('div'))
        total_elements = len(self.soup.find_all())
        if total_elements > 0 and (div_count / total_elements) > 0.7:
            score -= 5.0
        for form in self.soup.find_all('form'):
            for input_tag in form.find_all('input'):
                if not input_tag.get('id'):
                    score -= 1.0
        return score
    def responsive_eval(self, html_content):
        score = 0
        fixed_unit_penalty = 0
        style_text = html_content.lower()
        fixed_units = re.findall(r'(?:style\s*=\s*[\"\'][^\"\']*?)(\d+(px|pt|cm|mm))', style_text)
        if fixed_units:
            fixed_unit_penalty += len(fixed_units) * 1.5
        for style in self.soup.find_all('style'):
            if 'px' in style.text:
                fixed_unit_penalty += style.text.count('px') * 1.0
        score -= min(fixed_unit_penalty, 10.0)

        responsive_bonus = 0
        for unit in ['%', 'vw', 'vh', 'em', 'rem']:
            if unit in style_text:
                responsive_bonus += 0.5
        score += min(responsive_bonus, 2.5)
        return score
    def color_harmony_eval(self, html_content):
        score = 0
        color_values = self.extract_colors(html_content)
        harmony = self.color_harmony_score(color_values)
        if harmony < 0.4:
            score -= 5.0
        elif harmony > 0.8:
            score += 3.0
        elif harmony > 0.6:
            score += 1.5
        return score
    def css_eval(self, html_content):
        score = 0
        self.soup = BeautifulSoup(html_content, 'html.parser')
        style_tags = self.soup.find_all('style')
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
        return score
    
    def normalize_score(self, score):
        return max(0.0, min(score, 100.0)) / 100.0
    def eval(self):
        scores = []
        for html_content in self.responses:
            if "<html" not in html_content or "<body" not in html_content:
                scores.append(0.0)
                continue
            score = 100.0
            # 1. 구조 평가
            score += self.structure_eval(html_content)
            # 2. 반응형 단위 평가
            score += self.responsive_eval(html_content)
            # 3. 색상 조화도 평가
            score += self.color_harmony_eval(html_content)
            # 4. CSS 존재 여부 평가
            score += self.css_eval(html_content)
            # 최종 점수 정규화
            score = self.normalize_score(score)
            scores.append(score)
        return scores
    def new_eval(self):
        from bs4 import BeautifulSoup
        import re
        import colorsys
        import numpy as np
        from collections import Counter
        import math

        def extract_colors(css_text):
            hex_colors = re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}', css_text)
            rgb_colors = re.findall(r'rgb[a]?\(([^)]+)\)', css_text)
            rgb_colors = ['rgb(' + c + ')' for c in rgb_colors]
            return hex_colors + rgb_colors

        def color_to_hsl(color):
            try:
                if color.startswith('#'):
                    hex_color = color.lstrip('#')
                    if len(hex_color) == 3:
                        hex_color = ''.join([c*2 for c in hex_color])
                    r, g, b = [int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4)]
                elif color.startswith('rgb'):
                    nums = [int(n.strip()) for n in re.findall(r'\d+', color)[:3]]
                    r, g, b = [n / 255.0 for n in nums]
                else:
                    return None
                return colorsys.rgb_to_hls(r, g, b)
            except:
                return None

        def compute_color_harmony_score(colors):
            hsl_colors = [color_to_hsl(c) for c in colors]
            hsl_colors = [c for c in hsl_colors if c is not None]
            if len(hsl_colors) < 2:
                return 50
            hues = [c[0] for c in hsl_colors]
            lightness = [c[1] for c in hsl_colors]
            saturation = [c[2] for c in hsl_colors]
            hue_var = np.var(hues)
            light_var = np.var(lightness)
            sat_var = np.var(saturation)
            hue_score = 100 - min(hue_var * 200, 100)
            light_score = 100 - min(light_var * 300, 100)
            sat_score = 100 - min(sat_var * 300, 100)
            return round((hue_score * 0.4 + light_score * 0.3 + sat_score * 0.3), 2)

        def compute_layout_score(soup):
            divs = soup.find_all(['div', 'section', 'article', 'main', 'aside'])
            if not divs:
                return 50
            depths, widths, heights = [], [], []
            for div in divs:
                depth = len(list(div.parents))
                style = div.get('style', '')
                width = re.search(r'width\s*:\s*(\d+)', style)
                height = re.search(r'height\s*:\s*(\d+)', style)
                depths.append(depth)
                if width:
                    widths.append(int(width.group(1)))
                if height:
                    heights.append(int(height.group(1)))
            depth_score = 100 - min(np.std(depths) * 10, 50)
            width_score = 100 - min(np.std(widths) if widths else 50, 50)
            height_score = 100 - min(np.std(heights) if heights else 50, 50)
            return round((depth_score * 0.4 + width_score * 0.3 + height_score * 0.3), 2)

        def evaluate_responsiveness_score(soup, html_text):
            css_text = ''.join([tag.string or '' for tag in soup.find_all('style')])
            inline_styles = ' '.join([tag.get('style', '') for tag in soup.find_all(style=True)])
            full_style = (css_text + ' ' + inline_styles + ' ' + html_text).lower()

            # 1. 구조 기반 점수 (최대 50점)
            structural_score = 0
            if soup.find('meta', attrs={"name": "viewport"}):
                structural_score += 25
            if '@media' in full_style:
                structural_score += 25

            # 2. 고정 단위 감점 (최대 감점 20점)
            fixed_units = re.findall(r'(?:style\s*=\s*["\'][^"\']*?)(\d+(px|pt|cm|mm))', full_style)
            fixed_penalty = len(fixed_units) * 1.5
            fixed_penalty += full_style.count('px') * 0.5
            fixed_penalty = min(fixed_penalty, 20)

            # 3. 반응형 단위 보너스 (최대 30점)
            responsive_bonus = 0
            for unit in ['%', 'vw', 'vh', 'em', 'rem']:
                responsive_bonus += full_style.count(unit) * 0.2
            responsive_bonus = min(responsive_bonus, 30)

            # 종합 점수
            score = structural_score - fixed_penalty + responsive_bonus
            return round(max(0, min(score, 100)), 2)


        def evaluate_design_from_html(html_text):
            soup = BeautifulSoup(html_text, 'html.parser')
            css_text = ''.join([tag.string or '' for tag in soup.find_all('style')])
            inline_styles = ' '.join([tag.get('style', '') for tag in soup.find_all(style=True)])
            combined_css = css_text + ' ' + inline_styles

            colors = extract_colors(combined_css)
            color_score = compute_color_harmony_score(colors)
            layout_score = compute_layout_score(soup)
            responsive_score = evaluate_responsiveness_score(soup, html_text)

            # 새로운 가중치 기반 총점 (각 3분할)
            total_score = round((color_score * 0.34 + layout_score * 0.33 + responsive_score * 0.33), 2)

            return {
                "color_harmony": color_score,
                "layout": layout_score,
                "responsiveness": responsive_score,
                "total_score": total_score
            }


        results = []
        for html_content in self.responses:
            results.append(evaluate_design_from_html(html_content))
        return results
