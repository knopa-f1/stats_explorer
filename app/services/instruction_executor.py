import pandas as pd
from app.errors import InvalidInstructionError

class InstructionExecutor:
    allowed_operations = {
        "filter_then_aggregate",
        "filter_then_groupby",
        "groupby_compare",
        "groupby_stat",
        "groupby_extreme",
        "describe"
    }

    allowed_metrics = {
        "mean", "sum", "count", "percentage_of_total",
        "std", "min", "max", "difference_between_groups"
    }

    def execute(self, df: pd.DataFrame, instruction: dict):
        operation = instruction.get("operation")
        filters = instruction.get("filters", {})
        groupby = instruction.get("groupby")
        metric = instruction.get("metric")
        target_column = instruction.get("target_column")
        extreme = instruction.get("extreme")


        if operation not in self.allowed_operations:
            raise InvalidInstructionError(f"Операция '{operation}' не поддерживается.")

        if metric and metric not in self.allowed_metrics:
            raise InvalidInstructionError(f"Метрика '{metric}' не поддерживается.")

        df_filtered = self._apply_filters(df, filters)

        if operation == "filter_then_aggregate":
            return self._aggregate(df, df_filtered, metric, target_column)

        elif operation == "filter_then_groupby":
            return self._groupby(df_filtered, groupby, target_column, metric)

        elif operation == "groupby_compare":
            return self._groupby_compare(df, groupby, target_column)

        elif operation == "groupby_stat":
            return self._groupby_stat(df_filtered, groupby, target_column, metric)

        elif operation == "groupby_extreme":
            return self._groupby_extreme(df_filtered, groupby, target_column, metric, extreme)

        elif operation == "describe":
            return df_filtered[target_column].describe()

        raise InvalidInstructionError("Неизвестная комбинация operation + metric.")

    def _apply_filters(self, df: pd.DataFrame, filters: dict|None) -> pd.DataFrame:
        if filters is None:
            return df
        for column, condition in filters.items():
            if isinstance(condition, str) and condition.startswith("<"):
                value = float(condition[1:])
                df = df[df[column] < value]
            elif isinstance(condition, str) and condition.startswith(">"):
                value = float(condition[1:])
                df = df[df[column] > value]
            else:
                df = df[df[column] == condition]
        return df

    def _apply_metric(self, series_or_grouped, metric: str):
        if metric == "mean":
            return series_or_grouped.mean()
        if metric == "sum":
            return series_or_grouped.sum()
        if metric == "count":
            return series_or_grouped.count()
        if metric == "min":
            return series_or_grouped.min()
        if metric == "max":
            return series_or_grouped.max()
        if metric == "std":
            return series_or_grouped.std()
        raise InvalidInstructionError(f"Метрика '{metric}' не поддерживается.")

    def _aggregate(self, df: pd.DataFrame, filtered: pd.DataFrame, metric: str, target: str):
        if metric == "percentage_of_total":
            total = len(df)
            count = len(filtered)
            return f"{round((count / total) * 100, 2)}% строк удовлетворяют условию."
        return self._apply_metric(filtered[target], metric)

    def _groupby(self, df: pd.DataFrame, groupby: str, target: str, metric: str):
        grouped = df.groupby(groupby)[target]
        return self._apply_metric(grouped, metric)

    def _groupby_stat(self, df: pd.DataFrame, groupby: str, target: str, metric: str):
        grouped = df.groupby(groupby)[target]
        return self._apply_metric(grouped, metric)

    def _groupby_compare(self, df: pd.DataFrame, groupby: str, target: str):
        grouped = df.groupby(groupby)[target].mean().sort_values(ascending=False)
        if len(grouped) < 2:
            return "Недостаточно данных для сравнения."
        top, second = grouped.iloc[0], grouped.iloc[1]
        top_group = grouped.index[0]
        return f"{top_group} имеет на {round(top - second, 2)} больше, чем следующая группа."

    def _groupby_extreme(self, df: pd.DataFrame, groupby: str, target: str, metric: str, extreme: str):
        if extreme not in {"min", "max"}:
            raise InvalidInstructionError(f"Поле 'extreme' должно быть 'min' или 'max', получено: {extreme}")

        grouped = df.groupby(groupby)[target]
        result = self._apply_metric(grouped, metric)

        if result.empty:
            return "Нет данных для группировки."

        idx = result.idxmin() if extreme == "min" else result.idxmax()
        value = result.min() if extreme == "min" else result.max()
        return f"{idx} имеет {extreme} значение ({round(value, 2)}) по метрике '{metric}'."
