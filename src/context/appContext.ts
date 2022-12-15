import { CurrencyType } from "@coin-view/types";
import React from "react";

export const defaultCurrency = "PLN";

type AppContextType = {
  currency: CurrencyType;
  favorites?: any[];
};

export const AppContext = React.createContext<AppContextType>({
  currency: defaultCurrency,
  favorites: undefined,
});
