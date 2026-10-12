export type Product = {
  id: string; handle: string; name: string; purpose: string; price: number; mrp?: number;
  image: string; ingredient: string; format: string; concern: string; badge?: string; soldOut?: boolean;
  images?:string[];description?:string;status?:string;packSize: string; servings: number; origin: string; ritual: string; accent: string;
  packs: { id: string; sku?:string;label: string; detail: string;packSize?:string;servings?:number; price: number;mrp?:number;stock?:number }[];
};

export const concerns = ["Daily Wellness","Energy & Stamina","Digestion & Gut","Stress & Sleep","Immunity","Skin & Hair","Women's Wellness","Men's Vitality"];
export const ingredients = ["Moringa","Ashwagandha","Amla","Shilajit","Turmeric","Shatavari"];
export const articles = [
  {slug:"how-to-build-a-botanical-ritual",category:"Routines",title:"How to build a botanical ritual that lasts",summary:"A practical framework for choosing fewer, more intentional daily habits.",time:"5 min read"},
  {slug:"reading-a-wellness-label",category:"Product Guides",title:"A clear guide to reading a wellness label",summary:"Serving size, ingredient amounts and the details worth noticing.",time:"7 min read"},
  {slug:"ashwagandha-traditional-context",category:"Ingredients",title:"Ashwagandha: traditional context, modern use",summary:"What this well-known botanical is—and what responsible brands should never overclaim.",time:"6 min read"},
];

export const money = (n:number) => new Intl.NumberFormat("en-IN", {style:"currency",currency:"INR",maximumFractionDigits:0}).format(n);
