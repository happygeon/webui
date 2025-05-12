def html_structure_reward_func(completions, **kwargs) -> list[float]:
    """Improved HTML structure and responsiveness reward function"""
    from bs4 import BeautifulSoup
    import re

    responses = [completion[0]["content"] for completion in completions]
    scores = []

    for html_content in responses:
        try:
            # Check if valid HTML
            if "<html" not in html_content or "<body" not in html_content:
                scores.append(0.0)
                continue

            soup = BeautifulSoup(html_content, 'html.parser')
            score = 100.0

            # 1. Critical Structure Checks
            if not html_content.lower().startswith('<!doctype'):
                score -= 20.0  # Major loss

            html_tag = soup.find('html')
            if not html_tag or not html_tag.get('lang'):
                score -= 10.0

            if not soup.find('meta', attrs={'name': 'viewport'}):
                score -= 10.0

            # 2. Semantic Structure
            headings = soup.find_all(['h1', 'h2', 'h3'])
            if not headings:
                score -= 8.0
            elif not soup.find('h1'):
                score -= 5.0

            semantic_tags = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
            semantic_count = len(soup.find_all(semantic_tags))
            if semantic_count < 2:
                score -= 5.0

            # 3. Divitis penalty
            div_count = len(soup.find_all('div'))
            total_elements = len(soup.find_all())
            if total_elements > 0:
                div_ratio = div_count / total_elements
                if div_ratio > 0.7:
                    score -= 5.0  # lighter than before

            # 4. Form accessibility
            for form in soup.find_all('form'):
                for input_tag in form.find_all('input'):
                    if not input_tag.get('id'):
                        score -= 1.0  # mild accessibility issue

            # 5. Responsive design: discourage fixed units
            fixed_unit_penalty = 0
            style_text = html_content.lower()

            # Check for inline or <style> px usage
            fixed_units = re.findall(r'(?:style\s*=\s*["\'][^"\']*?)(\d+(px|pt|cm|mm))', style_text)
            if fixed_units:
                fixed_unit_penalty += len(fixed_units) * 1.5

            # Check for <style> blocks
            style_blocks = soup.find_all('style')
            for style in style_blocks:
                if 'px' in style.text:
                    fixed_unit_penalty += style.text.count('px') * 1.0

            score -= min(fixed_unit_penalty, 10.0)  # Cap penalty to 10

            # 6. Bonus: reward for responsive units
            responsive_bonus = 0
            responsive_units = ['%', 'vw', 'vh', 'em', 'rem']
            for unit in responsive_units:
                if unit in style_text:
                    responsive_bonus += 0.5  # max 2.5

            score += min(responsive_bonus, 2.5)

            # Normalize
            normalized_score = max(0.0, min(score, 100.0)) / 100.0
            scores.append(normalized_score)

        except Exception as e:
            print(f"[Parsing Error] {str(e)}")
            scores.append(0.0)

    return scores


