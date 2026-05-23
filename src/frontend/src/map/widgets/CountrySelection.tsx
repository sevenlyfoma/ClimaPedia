interface CountrySelectionProps {
  countryName: string;
  onReselect: () => void;
}

export default function CountrySelection(props: CountrySelectionProps) {
  return (
    <div className="country-selection">
      <p>
        Viewing <b>{props.countryName}</b>
      </p>
      <button onClick={props.onReselect}>Select new country</button>
    </div>
  );
}
