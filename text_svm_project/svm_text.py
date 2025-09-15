# -*- coding: utf-8 -*-
"""
SVM текстова класифікація (аналог R: quanteda + kernlab::ksvm)
- Вхід: TrainingData.csv (ID, month, year, three_sentences, цільові колонки)
- Вихід: Output.csv з доданими колонками predicted.values_<target>
"""

import os
import sys
import math
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold, cross_val_score

# --- 0) Налаштування ---
TRAINING_ROW = 6
TARGETS = ["THREAT_up", "THREAT_down", "citizen_impact", "PF_score", "PF_US", "PF_neg"]
INPUT_CSV  = "TrainingData.csv"
OUTPUT_CSV = "Output.csv"

def load_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        sys.exit(f"[ПОМИЛКА] Не знайдено файл: {path}. Поклади {path} у цю ж теку, де лежить svm_text.py")

    # пробуємо читати в UTF-8, якщо ні — fallback
    encodings_try = ["utf-8-sig", "utf-8", "cp1251"]
    last_err = None
    for enc in encodings_try:
        try:
            df = pd.read_csv(path, encoding=enc)
            return df
        except Exception as e:
            last_err = e
    raise last_err

def basic_clean(text_series: pd.Series) -> pd.Series:
    # до нижнього регістру + заміна пунктуації/не-слова на пробіли
    s = text_series.fillna("").astype(str).str.lower()
    s = s.str.replace(r"[^\w\s]", " ", regex=True)
    s = s.str.replace(r"\s+", " ", regex=True).str.strip()
    return s

def top_k_by_docfreq(texts: pd.Series, k: int = 200):
    """
    Обираємо топ-k термів за документною частотою (кількість документів, де терм зустрічається),
    як у твоєму R-пайплайні (docfreq).
    """
    cv = CountVectorizer(stop_words="english", token_pattern=r"(?u)\b\w+\b")
    Xc = cv.fit_transform(texts)
    # документна частота: скільки рядків мають терм > 0
    df = np.asarray((Xc > 0).sum(axis=0)).ravel()
    vocab = np.array(cv.get_feature_names_out())
    # сортуємо за DF спадно, беремо топ-k
    idx = np.argsort(-df)[: min(k, len(df))]
    top_terms = vocab[idx]
    return set(top_terms)

def build_tfidf(texts: pd.Series, top_terms: set):
    """
    Рахуємо TF-IDF тільки по відібраній лексиці (top_terms).
    """
    vocab = sorted(top_terms)  # стабільний порядок ознак
    tfidf = TfidfVectorizer(
        stop_words="english",
        token_pattern=r"(?u)\b\w+\b",
        vocabulary=vocab,
        use_idf=True,
        norm="l2"
    )
    X = tfidf.fit_transform(texts)
    feature_names = tfidf.get_feature_names_out()
    return X, feature_names

def main():
    df = load_data(INPUT_CSV)

    # Перевіримо наявність потрібних колонок
    needed_base = ["three_sentences"]
    missing = [c for c in needed_base if c not in df.columns]
    if missing:
        sys.exit(f"[ПОМИЛКА] У CSV немає потрібних колонок: {missing}. "
                 f"Мінімум потрібна 'three_sentences' + цільові колонки.")

    # залишимо базові колонки + таргети (як у R-версії)
    keep_cols = ["ID", "month", "year", "three_sentences"] + TARGETS
    keep_cols = [c for c in keep_cols if c in df.columns]
    df = df[keep_cols].copy()

    # Чистимо текст
    df["cleaned_body"] = basic_clean(df["three_sentences"])

    n = len(df)
    if n <= TRAINING_ROW:
        sys.exit(f"[ПОМИЛКА] Замало рядків ({n}). Потрібно > TRAINING_ROW={TRAINING_ROW}, "
                 f"щоб мати хоча б один тестовий приклад.")

    # --- Формуємо лексику топ-200 за документною частотою ---
    top_terms = top_k_by_docfreq(df["cleaned_body"], k=200)

    # --- TF-IDF матриця тільки по топовій лексиці ---
    X_all, feat_names = build_tfidf(df["cleaned_body"], top_terms)
    # у DataFrame для зручності (ksvm формула ~. в R аналогується повною матрицею ознак)
    X_df = pd.DataFrame(X_all.toarray(), columns=feat_names)

    # Train / Test спліт "зсувом": перші TRAINING_ROW — train
    X_train = X_df.iloc[:TRAINING_ROW, :].copy()
    X_test  = X_df.iloc[TRAINING_ROW:, :].copy()
    test_idx = np.arange(TRAINING_ROW, n)

    # Моделі та прогнози
    for target in TARGETS:
        if target not in df.columns:
            print(f"[ПОПЕРЕДЖЕННЯ] Колонки '{target}' немає у CSV — пропускаю.")
            continue

        y_raw = df.loc[:TRAINING_ROW - 1, target].copy()
        # NA -> 0, перетворення до {0,1}
        y_raw = y_raw.fillna(0).astype(str)
        # нормалізуємо можливі некоректні значення
        y = y_raw.where(y_raw.isin(["0", "1"]), other="0")

        # SVM RBF з імовірностями (як ksvm(..., prob.model=TRUE, kernel="rbfdot", C=50))
        clf = SVC(kernel="rbf", C=50, probability=True, random_state=42)

        # (необов’язково) 10-fold CV на train, як у cross=10 в ksvm
        try:
            skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
            cv_score = cross_val_score(clf, X_train, y, cv=skf, scoring="roc_auc")
            print(f"[{target}] CV AUC (10-fold): {cv_score.mean():.3f} ± {cv_score.std():.3f}")
        except Exception as e:
            print(f"[{target}] CV пропущено: {e}")

        # Навчання на всьому train і прогноз для test (ймовірність класу '1')
        clf.fit(X_train, y)
        probs = clf.predict_proba(X_test)[:, 1]  # колонка позитивного класу

        out_col = f"predicted.values_{target}"
        df[out_col] = np.nan
        df.loc[test_idx, out_col] = probs

    # Приберемо технічний стовпець cleaned_body (аналог cleaned.body у R)
    if "cleaned_body" in df.columns:
        df = df.drop(columns=["cleaned_body"])

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"[OK] Готово! Результати збережено у {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
