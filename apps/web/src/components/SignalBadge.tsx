import { AlertTriangle, CheckCircle2, HelpCircle, MinusCircle, Radio } from 'lucide-react';
import { SignalTier } from '../types';

export function tierColorHex(tier: SignalTier): string {
  switch (tier) {
    case 'Strong':
      return '#168A5B';
    case 'Good':
      return '#3978CF';
    case 'Fair':
      return '#D99C26';
    case 'Weak':
      return '#D95D54';
    default:
      return '#627D98';
  }
}

export function SignalBadge({ tier, size = 'sm' }: { tier: SignalTier; size?: 'sm' | 'lg' }) {
  const styles: Record<SignalTier, { bg: string; text: string; border: string; Icon: typeof CheckCircle2 }> = {
    Strong: { bg: 'bg-[#E6F4EE]', text: 'text-[#168A5B]', border: 'border-[#B7E1CD]', Icon: CheckCircle2 },
    Good: { bg: 'bg-[#EAF2FC]', text: 'text-[#3978CF]', border: 'border-[#BDD5F4]', Icon: Radio },
    Fair: { bg: 'bg-[#FCF5E6]', text: 'text-[#B47D14]', border: 'border-[#F2DBA8]', Icon: AlertTriangle },
    Weak: { bg: 'bg-[#FCECEB]', text: 'text-[#C2453D]', border: 'border-[#F3C2BF]', Icon: MinusCircle },
    Unavailable: { bg: 'bg-[#F0F4F8]', text: 'text-[#486581]', border: 'border-[#D9E2EC]', Icon: HelpCircle },
  };
  const { bg, text, border, Icon } = styles[tier] || styles.Unavailable;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-medium ${bg} ${text} ${border} ${
        size === 'lg' ? 'px-3.5 py-1.5 text-sm' : 'px-2.5 py-0.5 text-xs'
      }`}
    >
      <Icon className={size === 'lg' ? 'h-4 w-4' : 'h-3.5 w-3.5'} aria-hidden="true" />
      <span>{tier}</span>
    </span>
  );
}
