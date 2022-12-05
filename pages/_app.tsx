import "../styles/globals.css";
import type { AppProps } from "next/app";
import Script from "next/script";
import Head from "next/head";
import Image from "next/image";
import { CurrencyToggler, useCurrencyToggle } from "@coin-view/client";
import styles from "../styles/App.module.css";
import { useRouter } from "next/router";
import React from "react";
import { AppContext, defaultCurrency } from "@coin-view/context";

function MyApp({ Component, pageProps }: AppProps) {
  const GTM_ID = "G-R8PPSMRFS0";
  const { currency, toggleCurrency } = useCurrencyToggle(defaultCurrency);
  const { push } = useRouter();

  return (
    <>
      <Head>
        <title>Coin View</title>
        <meta name="description" content="Generated by create next app" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Script id="google-tag-manager" strategy="afterInteractive">
        {`
        (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
        new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
        j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
        'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
        })(window,document,'script','dataLayer','${GTM_ID}');
      `}
      </Script>

      <AppContext.Provider value={{ currency }}>
        <div className={styles.container}>
          <header className={styles.header}>
            <CurrencyToggler
              currency={currency}
              toggleCurrency={toggleCurrency}
            />
          </header>
          <main className={styles.main}>
            <div className={styles.mainLogo} onClick={() => push("/")}>
              <div className={styles.logoContainer}>
                <Image
                  src="/logo-square.svg"
                  alt="logo"
                  width={100}
                  height={100}
                  layout="responsive"
                />
              </div>
              <h1 className={styles.title}>Coin View</h1>
            </div>
            <Component {...pageProps} />
          </main>
          <footer className={styles.footer}>CoinView®</footer>
        </div>
      </AppContext.Provider>
    </>
  );
}

export default MyApp;
